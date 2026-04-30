from app.services.ai_service import ai_service
from app.models import StoryResponse
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
            print(f"--- Pausa detectada. Analizando interacción ---")
            # Separar historia del resto
            partes = texto_limpio.split("[PAUSA_INTERACCION]")
            historia_limpia = partes[0].strip()
            resto = partes[1].strip() if len(partes) > 1 else "¿Qué quieres que pase ahora?"
            
            # Buscar opciones: Intentar con tag literal o buscando el patrón "A | B"
            opciones = []
            prompt_interaccion = resto

            if "[OPCIONES]" in resto:
                partes_opciones = resto.split("[OPCIONES]")
                prompt_interaccion = partes_opciones[0].strip()
                texto_opciones = partes_opciones[1].strip()
            elif "|" in resto:
                # Si no hay tag pero hay pipes, intentamos separar por líneas
                lineas = resto.split('\n')
                prompt_interaccion = lineas[0].strip()
                texto_opciones = " ".join(lineas[1:]) if len(lineas) > 1 else lineas[0]
                # Si el pipe está en la misma línea que el prompt, re-ajustamos
                if "|" in prompt_interaccion and len(lineas) == 1:
                    partes_pipe = prompt_interaccion.split("|", 1) # Solo el primer pipe para separar prompt de la primera opcion? No
                    # Mejor buscar el primer pipe y ver si antes hay una interrogación
                    match = re.search(r'([¿?].*?)(\b[^¿?]*?\|.*)', prompt_interaccion)
                    if match:
                        prompt_interaccion = match.group(1).strip()
                        texto_opciones = match.group(2).strip()
                    else:
                        # Fallback simple: separar por el primer pipe
                        partes_pipe = prompt_interaccion.split("|")
                        prompt_interaccion = "¿Qué pasará ahora?"
                        texto_opciones = resto
            else:
                texto_opciones = ""

            # Extraer opciones del bloque de texto detectado
            if "|" in texto_opciones:
                opciones = [opt.strip().replace("[OPCIONES]", "") for opt in texto_opciones.split("|") if opt.strip()]
            
            # Limpieza final del prompt
            prompt_interaccion = prompt_interaccion.replace("[OPCIONES]", "").strip()
            
            # Si después de todo no hay opciones, creamos unas por defecto para no romper el flujo
            if not opciones:
                opciones = ["Continuar la aventura", "Ver qué pasa después"]

            print(f"Prompt: {prompt_interaccion}")
            print(f"Opciones: {opciones}")
            
            return StoryResponse(
                historia=historia_limpia,
                audio_text=historia_limpia,
                necesita_interaccion=True,
                prompt_interaccion=prompt_interaccion,
                opciones=opciones,
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
            historia_completa=historia_actual, 
            eleccion_usuario=nuevo_personaje, 
            edad=edad, 
            interaccion_numero=interaccion_numero
        )
        
        return self.parsear_historia(continuacion_raw, edad, interaccion_numero)


story_service = StoryService()