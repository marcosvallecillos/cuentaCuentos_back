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
        protagonistas = crud.get_catalog_items(db, tipo=models.CatalogType.PROTAGONISTA)
        lugares = crud.get_catalog_items(db, tipo=models.CatalogType.LUGAR)
        emociones = crud.get_catalog_items(db, tipo=models.CatalogType.EMOCION)
        
        context = "\n\nCONTEXTO DE CATÁLOGO DISPONIBLE:\n"
        
        if protagonistas:
            context += "Protagonistas sugeridos: " + ", ".join([p.nombre for p in protagonistas[:10]]) + "\n"
        
        if lugares:
            context += "Lugares mágicos: " + ", ".join([l.nombre for l in lugares[:10]]) + "\n"
        
        if emociones:
            context += "Emociones a explorar: " + ", ".join([e.nombre for e in emociones[:10]]) + "\n"
        
        return context
    
    def generar_historia_inicial(self, objeto: str, edad: int, db: Optional[Session] = None) -> str:
        """Genera el inicio de una historia interactiva"""
        config = self.get_age_config(edad)
        
        prompt = f"""Eres un narrador mágico de cuentos infantiles. 
        
        PERSONAJE PRINCIPAL: {personaje}
        LUGAR: {lugar}
        EMOCIÓN: {emocion}
        EDAD DEL NIÑO: {edad} años
        VOCABULARIO: {config['vocabulary']}
        LONGITUD: aproximadamente {config['story_length']} palabras
        
        INSTRUCCIONES CRÍTICAS:
        1. Crea el INICIO de una historia mágica donde el protagonista es "{personaje}", sucede en "{lugar}" y el tono es "{emocion}".
        2. Usa lenguaje {config['vocabulary']} apropiado para {edad} años.
        3. Después de 3-4 oraciones, DEBES incluir EXACTAMENTE esta marca: [PAUSA_INTERACCION]
        4. Justo después de la pausa, escribe una pregunta invitando al niño a elegir quién aparecerá ahora.
           Ejemplo: "¿Quién crees que aparecerá ahora para ayudar a Sol?"
        5. La historia debe quedar ABIERTA, lista para continuar.
        6. NO termines la historia, solo el primer acto.
        
        FORMATO EXACTO:
        [Inicio de la historia]
        [PAUSA_INTERACCION]
        [Pregunta para elegir siguiente paso]
        [OPCIONES] Opción corta 1 | Opción corta 2
        
        AHORA, crea la historia para "{personaje}" en "{lugar}":"""

        print(f"--- Generando inicio para {personaje} en {lugar} ---")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        print("--- Historia generada con éxito ---")
        return completion.choices[0].message.content.strip()


    
    def continuar_historia(self, historia_actual: str, nuevo_personaje: str, 
                          edad: int, interaccion_numero: int) -> str:
        """Continúa la historia incorporando el nuevo personaje elegido"""
        config = self.get_age_config(edad)
        max_interactions = config['interactions']
        es_ultima = interaccion_numero >= max_interactions
        
        prompt = f"""Eres un narrador mágico continuando un cuento infantil.

        HISTORIA HASTA AHORA:
        {historia_actual}

        NUEVO PERSONAJE QUE APARECE: {nuevo_personaje}
        EDAD: {edad} años
        INTERACCIÓN: {interaccion_numero} de {max_interacciones}
        ES LA ÚLTIMA: {"SÍ" if es_ultima_interaccion else "NO"}

        INSTRUCCIONES:
        1. Integra naturalmente a "{nuevo_personaje}" en la historia.
        2. Continúa con 3-4 oraciones.
        3. {"Concluye la historia con un final feliz y mágico" if es_ultima_interaccion else "Incluye [PAUSA_INTERACCION] y otra pregunta para elegir el siguiente paso"}

        FORMATO:
        [Continuación natural integrando {nuevo_personaje}]
        {"[FIN]" if es_ultima_interaccion else "[PAUSA_INTERACCION]\n[Nueva pregunta de elección]\n[OPCIONES] Opción corta 1 | Opción corta 2"}

        CONTINÚA LA HISTORIA:"""

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        return completion.choices[0].message.content.strip()

    
    def detectar_objeto_en_dibujo(self, descripcion_usuario: str) -> str:
        """
        En producción, aquí integrarías visión por computadora.
        Para MVP, usamos descripción del usuario.
        """
        # TODO: Integrar Google Vision API o similar
        return descripcion_usuario.lower()

ai_service = AIService()