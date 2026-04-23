from app.services.ai_service import ai_service
from app.models import StoryResponse
import re

class StoryService:
    
    def parsear_historia(self, texto_historia: str, edad: int, 
                        interaccion_numero: int) -> StoryResponse:
        """Parsea la historia y detecta puntos de interacción"""
        
        # Buscar marca de pausa
        tiene_pausa = "[PAUSA_INTERACCION]" in texto_historia
        es_final = "[FIN]" in texto_historia
        
        if es_final:
            # Historia terminada
            historia_limpia = texto_historia.replace("[FIN]", "").strip()
            return StoryResponse(
                historia=historia_limpia,
                audio_text=historia_limpia,
                necesita_interaccion=False,
                prompt_interaccion=None,
                progreso={
                    "completado": True,
                    "interaccion_actual": interaccion_numero
                }
            )
        
        if tiene_pausa:
            # Separar historia del prompt
            partes = texto_historia.split("[PAUSA_INTERACCION]")
            historia_limpia = partes[0].strip()
            prompt_interaccion = partes[1].strip() if len(partes) > 1 else "¿Qué aparece ahora? ¡Dibújalo!"
            
            return StoryResponse(
                historia=historia_limpia,
                audio_text=historia_limpia,
                necesita_interaccion=True,
                prompt_interaccion=prompt_interaccion,
                progreso={
                    "completado": False,
                    "interaccion_actual": interaccion_numero
                }
            )
        
        # Sin pausa ni fin (caso edge)
        return StoryResponse(
            historia=texto_historia,
            audio_text=texto_historia,
            necesita_interaccion=False,
            prompt_interaccion=None,
            progreso={
                "completado": True,
                "interaccion_actual": interaccion_numero
            }
        )
    
    def crear_historia_inicial(self, personaje: str, lugar: str, emocion: str, edad: int) -> StoryResponse:
        """Genera la historia inicial basada en las selecciones"""
        historia_raw = ai_service.generar_historia_inicial(personaje, lugar, emocion, edad)
        return self.parsear_historia(historia_raw, edad, 0)
    
    def continuar_historia(self, historia_actual: str, nuevo_personaje: str,
                          edad: int, interaccion_numero: int) -> StoryResponse:
        """Continúa la historia con el nuevo personaje elegido"""
        continuacion_raw = ai_service.continuar_historia(
            historia_actual, nuevo_personaje, edad, interaccion_numero
        )
        
        return self.parsear_historia(continuacion_raw, edad, interaccion_numero)


story_service = StoryService()