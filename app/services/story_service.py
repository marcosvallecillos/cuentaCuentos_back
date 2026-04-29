from app.services.ai_service import ai_service
from app.schemas import StoryResponse
import re

class StoryService:
    
    def parsear_historia(self, texto_historia: str, edad: int, 
                        interaccion_numero: int) -> StoryResponse:
        """Parsea la historia y detecta puntos de interacción"""
        
        # Limpiar etiquetas comunes que la IA a veces incluye por error en el texto final
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
            # Separar historia del resto
            partes = texto_limpio.split("[PAUSA_INTERACCION]")
            historia_limpia = partes[0].strip()
            resto = partes[1].strip() if len(partes) > 1 else "¿Qué quieres que pase ahora?"
            
            # Buscar opciones
            opciones = []
            prompt_interaccion = resto
            
            if "[OPCIONES]" in resto:
                partes_opciones = resto.split("[OPCIONES]")
                prompt_interaccion = partes_opciones[0].strip()
                texto_opciones = partes_opciones[1].strip()
                # Separar por | o por saltos de línea o por números
                if "|" in texto_opciones:
                    opciones = [opt.strip() for opt in texto_opciones.split("|") if opt.strip()]
                else:
                    # Intento de separar por líneas si no hay pipe
                    opciones = [opt.strip() for opt in texto_opciones.split("\n") if opt.strip()][:2]
            
            # Limpiar el prompt de la etiqueta OPCIONES si quedó algo
            prompt_interaccion = prompt_interaccion.replace("[OPCIONES]", "").strip()
            
            return StoryResponse(
                historia=historia_limpia,
                audio_text=historia_limpia,
                necesita_interaccion=True,
                prompt_interaccion=prompt_interaccion,
                opciones=opciones if len(opciones) >= 2 else None,
                progreso={
                    "completado": False,
                    "interaccion_actual": interaccion_numero
                }
            )
        
        # Sin pausa ni fin (caso edge)
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
            historia_actual, nuevo_personaje, edad, interaccion_numero
        )
        
        return self.parsear_historia(continuacion_raw, edad, interaccion_numero)


story_service = StoryService()