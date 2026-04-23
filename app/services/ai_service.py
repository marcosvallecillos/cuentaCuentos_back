import google.generativeai as genai
from app.config import settings
from typing import Dict

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
    
    def generar_historia_inicial(self, personaje: str, lugar: str, emocion: str, edad: int) -> str:
        """Genera el inicio de una historia interactiva basada en selecciones"""
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
        [Pregunta para elegir siguiente personaje]
        
        AHORA, crea la historia para "{personaje}" en "{lugar}":"""

        response = self.model.generate_content(prompt)
        return response.text.strip()

    
    def continuar_historia(self, historia_actual: str, nuevo_personaje: str, 
                          edad: int, interaccion_numero: int) -> str:
        """Continúa la historia incorporando el nuevo personaje elegido"""
        config = self.get_age_config(edad)
        max_interacciones = config['interactions']
        
        es_ultima_interaccion = interaccion_numero >= max_interacciones
        
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
        {"[FIN]" if es_ultima_interaccion else "[PAUSA_INTERACCION]\n[Nueva pregunta de elección]"}

        CONTINÚA LA HISTORIA:"""

        response = self.model.generate_content(prompt)
        return response.text.strip()

    
    def detectar_objeto_en_dibujo(self, descripcion_usuario: str) -> str:
        """
        En producción, aquí integrarías visión por computadora.
        Para MVP, usamos descripción del usuario.
        """
        # TODO: Integrar Google Vision API o similar
        return descripcion_usuario.lower()

ai_service = AIService()