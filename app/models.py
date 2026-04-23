from pydantic import BaseModel, Field
from typing import Optional, List

class StoryRequest(BaseModel):
    personaje: str = Field(..., description="Personaje principal (ej. León)")
    lugar: str = Field(..., description="Lugar del cuento (ej. Bosque)")
    emocion: str = Field(..., description="Emoción predominante (ej. Feliz)")
    edad: int = Field(..., ge=3, le=12, description="Edad del niño")
    
class ContinueStoryRequest(BaseModel):
    historia_actual: str = Field(..., description="Historia hasta el momento")
    nuevo_objeto: str = Field(..., description="Nuevo objeto dibujado")
    edad: int = Field(..., ge=3, le=12)
    interaccion_numero: int = Field(default=1, description="Número de interacción")

class StoryResponse(BaseModel):
    historia: str
    audio_text: str
    necesita_interaccion: bool
    prompt_interaccion: Optional[str] = None
    opciones: Optional[List[str]] = None
    progreso: dict

class StorySegment(BaseModel):
    texto: str
    requiere_pausa: bool
    prompt_usuario: Optional[str] = None