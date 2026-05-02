from app.services.ai_service import ai_service
from pydantic import BaseModel
from typing import Optional
import re

class StoryResponse(BaseModel):
    historia: str
    audio_text: str
    necesita_interaccion: bool
    prompt_interaccion: Optional[str] = None
    opciones: list[str] = []
    progreso: dict

class StoryService:
    
    def parsear_historia(self, texto_historia: str, edad: int, 
                        interaccion_numero: int) -> StoryResponse:
        """Parsea la historia y detecta puntos de interacción y opciones"""
        
        # 1. Limpiar etiquetas de estructura que la IA a veces incluye literalmente
        # Quitamos cualquier bloque entre corchetes al inicio que parezca técnico
        texto_limpio = re.sub(r'^\[(NARRATIVA|CONTINUACION|INICIO)[^\]]*\]\s*', '', texto_historia, flags=re.IGNORECASE)
        
        # Limpiar otras etiquetas comunes
        etiquetas_a_borrar = [
            "[Inicio de la historia]", "[Continuación natural]", "[Continuacion natural]",
            "[Continuacion natural integrando la eleccion]", "[NARRATIVA]", "[Narrativa]"
        ]
        for tag in etiquetas_a_borrar:
            texto_limpio = texto_limpio.replace(tag, "")
            
        # Limpiar cualquier cosa que empiece con "[Continuacion natural integrando..."
        texto_limpio = re.sub(r'\[Continuacion natural integrando[^\]]*\]', '', texto_limpio).strip()
        
        # Buscar marcas
        tiene_opciones = "[OPCIONES]" in texto_limpio
        es_final = "[FIN]" in texto_limpio or "[FINAL]" in texto_limpio
        
        if es_final:
            # Historia terminada
            historia_final = texto_limpio.split("[FIN]")[0].split("[FINAL]")[0].strip()
            # Limpiar posibles corchetes residuales
            historia_final = re.sub(r'\[[^\]]*\]', '', historia_final).strip()
            
            return StoryResponse(
                historia=historia_final,
                audio_text=historia_final,
                necesita_interaccion=False,
                prompt_interaccion=None,
                opciones=[],
                progreso={
                    "completado": True,
                    "interaccion_actual": interaccion_numero
                }
            )
        
        if tiene_opciones:
            print(f"--- Opciones detectadas en historia ---")
            partes = texto_limpio.split("[OPCIONES]")
            historia_limpia = partes[0].strip()
            # Limpiar posibles corchetes residuales en la historia
            historia_limpia = re.sub(r'\[[^\]]*\]', '', historia_limpia).strip()
            
            resto = partes[1].strip() if len(partes) > 1 else ""
            
            lineas = [l.strip() for l in resto.split("\n") if l.strip()]
            
            # El prompt es la primera línea que no sea un placeholder
            prompt_interaccion = "¿Qué quieres que pase ahora?"
            opciones_inicio_idx = 0
            
            for i, linea in enumerate(lineas):
                if "[Pregunta de seguimiento]" in linea or "[PREGUNTA]" in linea:
                    continue
                if not any(linea.startswith(prefix) for prefix in ["1.", "2.", "3.", "4.", "-"]):
                    prompt_interaccion = linea
                    opciones_inicio_idx = i + 1
                    break
            
            # Extraer opciones (líneas que empiezan con número o guión)
            opciones = []
            for linea in lineas[opciones_inicio_idx:]:
                # Ignorar placeholders literales
                if "[Pregunta de seguimiento]" in linea or "[Opcion" in linea:
                    continue
                    
                # Limpiar números (1., 1-, etc) o guiones al inicio
                opc = re.sub(r'^(\d+[\.\-\)]\s*|-\s*)', '', linea).strip()
                if opc and len(opc) > 2: # Evitar opciones demasiado cortas o vacías
                    opciones.append(opc)
            
            # Si no se detectaron opciones claras, usar las 3 primeras líneas después del prompt
            if not opciones and len(lineas) > opciones_inicio_idx:
                for l in lineas[opciones_inicio_idx:opciones_inicio_idx+3]:
                    if "[" not in l:
                        opciones.append(l)

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
        
        # Caso genérico - Limpiar cualquier corchete que haya quedado
        texto_limpio = re.sub(r'\[[^\]]*\]', '', texto_limpio).strip()

        return StoryResponse(
            historia=texto_limpio,
            audio_text=texto_limpio,
            necesita_interaccion=False,
            prompt_interaccion=None,
            opciones=[],
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