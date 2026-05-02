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
        
        # Limpiar etiquetas comunes que la IA a veces incluye
        texto_limpio = texto_historia.replace("[Inicio de la historia]", "").replace("[Continuación natural]", "").strip()
        
        # Buscar marcas
        tiene_opciones = "[OPCIONES]" in texto_limpio
        es_final = "[FIN]" in texto_limpio or "[FINAL]" in texto_limpio
        
        if es_final:
            # Historia terminada
            historia_final = texto_limpio.split("[FIN]")[0].split("[FINAL]")[0].strip()
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
            # Separar historia, prompt y opciones
            # Formato esperado:
            # Historia...
            # [OPCIONES]
            # ¿Qué quieres hacer?
            # 1. Opción A
            # 2. Opción B
            # 3. Opción C
            
            partes = texto_limpio.split("[OPCIONES]")
            historia_limpia = partes[0].strip()
            resto = partes[1].strip() if len(partes) > 1 else ""
            
            lineas = [l.strip() for l in resto.split("\n") if l.strip()]
            prompt_interaccion = lineas[0] if lineas else "¿Qué quieres que pase ahora?"
            
            # Extraer opciones (líneas que empiezan con número o guión)
            opciones = []
            for linea in lineas[1:]:
                # Limpiar números (1., 1-, etc) o guiones al inicio
                opc = re.sub(r'^(\d+[\.\-\)]\s*|-\s*)', '', linea).strip()
                if opc:
                    opciones.append(opc)
            
            # Si no se detectaron opciones claras, usar las 3 primeras líneas después del prompt
            if not opciones and len(lineas) > 1:
                opciones = lineas[1:4]

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
        
        # Caso genérico o marca antigua [PAUSA_INTERACCION]
        if "[PAUSA_INTERACCION]" in texto_limpio:
            partes = texto_limpio.split("[PAUSA_INTERACCION]")
            return StoryResponse(
                historia=partes[0].strip(),
                audio_text=partes[0].strip(),
                necesita_interaccion=True,
                prompt_interaccion=partes[1].strip() if len(partes) > 1 else "¿Qué pasa después?",
                opciones=["Continuar la aventura"],
                progreso={"completado": False, "interaccion_actual": interaccion_numero}
            )

        # Sin pausa ni fin
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