from groq import Groq
from app.config import settings
from typing import Dict
class AIService:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.1-8b-instant"
        print("✅ Groq inicializado")
    
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
        
        system_prompt = f"""Eres un narrador de cuentos infantiles experto en crear mundos mágicos y coherentes. 
        Tu objetivo es cautivar a niños de {edad} años usando un vocabulario {config['vocabulary']}.
        Mantén siempre un tono cálido, descriptivo y lleno de maravilla."""

        user_prompt = f"""Crea el INICIO de una historia mágica.
        
        PERSONAJE PRINCIPAL: {personaje}
        LUGAR: {lugar}
        EMOCIÓN: {emocion}
        EDAD DEL NIÑO: {edad} años
        
        INSTRUCCIONES:
        1. Comienza la aventura de forma emocionante.
        2. Después de 3-4 oraciones descriptivas, DEBES incluir EXACTAMENTE esta marca: [PAUSA_INTERACCION]
        3. Justo después, haz una pregunta directa al niño para que elija qué sucede a continuación o quién aparece.
        4. Define dos opciones claras y cortas.
        
        FORMATO:
        [Texto de la historia]
        [PAUSA_INTERACCION]
        ¿A quién encontrará {personaje} ahora?
        [OPCIONES] Opción A | Opción B
        """

        print(f"--- Generando inicio para {personaje} en {lugar} ---")
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        return completion.choices[0].message.content.strip()

    def continuar_historia(self, historia_completa: str, eleccion_usuario: str, 
                          edad: int, interaccion_numero: int) -> str:
        """Continúa la historia basándose en todo el contexto previo"""
        config = self.get_age_config(edad)
        max_interactions = config['interactions']
        es_ultima = interaccion_numero >= max_interactions
        
        system_prompt = f"""Eres un narrador de cuentos infantiles para niños de {edad} años. 
        Debes mantener la COHERENCIA total con lo que ha sucedido antes.
        Usa vocabulario {config['vocabulary']}. """

        status_msg = "Este es el FINAL del cuento. Concluye de forma hermosa y cerrada." if es_ultima else "Continúa la aventura y termina con una nueva elección."
        
        user_prompt = f"""HISTORIA HASTA AHORA:
        {historia_completa}

        LO QUE EL NIÑO ELIGIÓ: "{eleccion_usuario}"

        INSTRUCCIONES:
        1. Integra la elección "{eleccion_usuario}" de forma fluida y mágica.
        2. Escribe 4-5 oraciones que avancen la trama.
        3. {status_msg}
        
        FORMATO SI NO ES EL FINAL:
        [Continuación del cuento]
        [PAUSA_INTERACCION]
        [Pregunta de elección]
        [OPCIONES] Opción 1 | Opción 2

        FORMATO SI ES EL FINAL:
        [Final del cuento]
        [FIN]
        """

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
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