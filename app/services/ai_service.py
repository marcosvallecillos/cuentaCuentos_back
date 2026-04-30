import google.generativeai as genai
from app.config import settings
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app import crud, models

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def get_age_group(self, edad: int) -> str:
        """Determina el grupo de edad"""
        if 3 <= edad <= 5:
            return "3-5"
        elif 6 <= edad <= 8:
            return "6-8"
        else:
            return "9-12"
    
    def get_age_config(self, edad: int) -> Dict:
        """Obtiene configuración según edad"""
        group = self.get_age_group(edad)
        return settings.AGE_GROUPS[group]
    
    def get_catalog_context(self, db: Session) -> str:
        """Obtener contexto del catálogo para enriquecer prompts"""
        try:
            protagonistas = crud.get_catalog_items(db, tipo=models.CatalogType.PROTAGONISTA)
            lugares = crud.get_catalog_items(db, tipo=models.CatalogType.LUGAR)
            emociones = crud.get_catalog_items(db, tipo=models.CatalogType.EMOCION)
            
            context = "\n\nCONTEXTO DE CATALOGO DISPONIBLE:\n"
            
            if protagonistas:
                context += "Protagonistas sugeridos: " + ", ".join([p.nombre for p in protagonistas[:10]]) + "\n"
            
            if lugares:
                context += "Lugares magicos: " + ", ".join([l.nombre for l in lugares[:10]]) + "\n"
            
            if emociones:
                context += "Emociones a explorar: " + ", ".join([e.nombre for e in emociones[:10]]) + "\n"
            
            return context
        except Exception as e:
            print(f"⚠️ Error obteniendo catalogo: {e}")
            return ""
    
    def generar_historia_inicial(self, objeto: str, edad: int, db: Optional[Session] = None) -> str:
        """Genera el inicio de una historia interactiva"""
        config = self.get_age_config(edad)
        
        # Contexto adicional del catálogo
        catalog_context = ""
        if db:
            catalog_context = self.get_catalog_context(db)
            # Incrementar uso si el objeto está en el catálogo
            try:
                crud.increment_catalog_usage(db, objeto)
            except Exception as e:
                print(f"⚠️ No se pudo incrementar uso del catalogo: {e}")
        
        prompt = f"""Eres un narrador magico de cuentos infantiles. 

PERSONAJE PRINCIPAL: {objeto}
EDAD DEL NINO: {edad} años
VOCABULARIO: {config['vocabulary']}
LONGITUD: aproximadamente {config['story_length']} palabras
{catalog_context}

INSTRUCCIONES CRITICAS:
1. Crea el INICIO de una historia magica sobre "{objeto}"
2. Usa lenguaje {config['vocabulary']} apropiado para {edad} años
3. Despues de 3-4 oraciones, DEBES incluir EXACTAMENTE esta marca: [PAUSA_INTERACCION]
4. Justo despues de la pausa, escribe una pregunta invitando al nino a dibujar algo nuevo
   Ejemplo: "Quien crees que aparecera ahora? Dibujalo!"
5. La historia debe quedar ABIERTA, lista para continuar
6. NO termines la historia, solo el primer acto

FORMATO EXACTO:
[Inicio de la historia con 3-4 oraciones]
[PAUSA_INTERACCION]
[Pregunta invitando a dibujar]

Ejemplo para "pollito":
"Habia una vez un pollito amarillo llamado Sol que vivia en una granja magica. Una manana, Sol decidio explorar el bosque cercano. Mientras caminaba entre las flores, escucho un ruido extrano detras de los arbustos.
[PAUSA_INTERACCION]
Que crees que encontro Sol? Dibuja al nuevo amigo que aparecera!"

AHORA, crea la historia para "{objeto}":"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Error llamando a Gemini API: {e}")
            raise Exception(f"Error generando historia con IA: {str(e)}")
    
    def continuar_historia(self, historia_actual: str, nuevo_objeto: str, 
                          edad: int, interaccion_numero: int, 
                          db: Optional[Session] = None) -> str:
        """Continúa la historia incorporando el nuevo objeto"""
        config = self.get_age_config(edad)
        max_interacciones = config['interactions']
        
        es_ultima_interaccion = interaccion_numero >= max_interacciones
        
        # Incrementar uso si está en catálogo
        if db:
            try:
                crud.increment_catalog_usage(db, nuevo_objeto)
            except Exception as e:
                print(f"⚠️ No se pudo incrementar uso del catalogo: {e}")
        
        # Construir el prompt SIN acentos en las palabras clave del template
        if es_ultima_interaccion:
            formato_respuesta = "[FIN]"
            instruccion_3 = "Concluye la historia con un final feliz y magico. Usa la marca [FIN]"
        else:
            formato_respuesta = "[PAUSA_INTERACCION]\n[Nueva pregunta para dibujar]"
            instruccion_3 = "Incluye [PAUSA_INTERACCION] y otra pregunta para dibujar"
        
        prompt = f"""Eres un narrador magico continuando un cuento infantil.

HISTORIA HASTA AHORA:
{historia_actual}

NUEVO ELEMENTO DIBUJADO: {nuevo_objeto}
EDAD: {edad} años
INTERACCION: {interaccion_numero} de {max_interacciones}
ES LA ULTIMA: {"SI" if es_ultima_interaccion else "NO"}

INSTRUCCIONES:
1. Integra naturalmente "{nuevo_objeto}" en la historia
2. Continua con 3-4 oraciones
3. {instruccion_3}

FORMATO:
[Continuacion natural integrando {nuevo_objeto}]
{formato_respuesta}

CONTINUA LA HISTORIA:"""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"❌ Error llamando a Gemini API: {e}")
            raise Exception(f"Error continuando historia con IA: {str(e)}")
    
    def detectar_objeto_en_dibujo(self, descripcion_usuario: str) -> str:
        """
        En producción, aquí integrarías visión por computadora.
        Para MVP, usamos descripción del usuario.
        """
        # TODO: Integrar Google Vision API o similar
        return descripcion_usuario.lower()

ai_service = AIService()