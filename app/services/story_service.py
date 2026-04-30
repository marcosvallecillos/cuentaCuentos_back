from app.services.ai_service import ai_service
from pydantic import BaseModel
from typing import Optional
import re

class StoryResponse(BaseModel):
    historia: str
    audio_text: str
    necesita_interaccion: bool
    prompt_interaccion: Optional[str] = None
    progreso: dict

class StoryService:
    
    def parsear_historia(self, texto_historia: str, edad: int, 
                        interaccion_numero: int) -> StoryResponse:
        """Parsea la historia y detecta puntos de interacción"""
        
        # Limpiar etiquetas comunes que la IA a veces incluye
        texto_limpio = texto_historia.replace("[Inicio de la historia]", "").replace("[Continuación natural]", "").strip()
        
        # Buscar marca de pausa
        tiene_pausa = "[PAUSA_INTERACCION]" in texto_limpio
        es_final = "[FIN]" in texto_limpio or "[FINAL]" in texto_limpio
        
        if es_final:
            # Historia terminada
            historia_final = texto_limpio.replace("[FIN]", "").replace("[FINAL]", "").strip()
            return StoryResponse(
                historia=historia_final,
                audio_text=historia_final,
                necesita_interaccion=False,
                prompt_interaccion=None,
                progreso={
                    "completado": True,
                    "interaccion_actual": interaccion_numero
                }
            )
        
        if tiene_pausa:
            print(f"--- Pausa detectada en historia ---")
            # Separar historia del prompt
            partes = texto_limpio.split("[PAUSA_INTERACCION]")
            historia_limpia = partes[0].strip()
            prompt_interaccion = partes[1].strip() if len(partes) > 1 else "¿Qué aparece ahora? ¡Dibújalo!"
            
            print(f"Prompt de interacción: {prompt_interaccion}")
            
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
        
        # Sin pausa ni fin (caso edge - historia completa sin marca)
        print("⚠️ Historia sin marca de pausa ni fin")
        return StoryResponse(
            historia=texto_limpio,
            audio_text=texto_limpio,
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
            historia_completa=historia_actual, 
            eleccion_usuario=nuevo_personaje, 
            edad=edad, 
            interaccion_numero=interaccion_numero
        )
        
        return self.parsear_historia(continuacion_raw, edad, interaccion_numero)


story_service = StoryService()