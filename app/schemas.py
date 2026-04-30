from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models import CatalogType

# ============= STORY SCHEMAS =============

class StoryInteractionBase(BaseModel):
    orden: int
    objeto_dibujado: str
    texto_generado: str

class StoryInteractionCreate(StoryInteractionBase):
    pass

class StoryInteractionResponse(StoryInteractionBase):
    id: int
    story_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class StoryCreate(BaseModel):
    edad_usuario: int
    grupo_edad: str
    texto_completo: str
    duracion_segundos: Optional[int] = None

class StoryResponse(BaseModel):
    id: int
    edad_usuario: int
    grupo_edad: str
    texto_completo: str
    created_at: datetime
    duracion_segundos: Optional[int]
    interacciones: List[StoryInteractionResponse] = []
    
    class Config:
        from_attributes = True

class StoryListResponse(BaseModel):
    id: int
    edad_usuario: int
    grupo_edad: str
    preview: str  # Primeras 100 chars
    created_at: datetime
    num_interacciones: int
    
    class Config:
        from_attributes = True

# ============= CATALOG SCHEMAS =============

class CatalogItemBase(BaseModel):
    tipo: CatalogType
    nombre: str
    descripcion: Optional[str] = None
    emoji: Optional[str] = None
    prompt_sugerencia: Optional[str] = None

class CatalogItemCreate(CatalogItemBase):
    pass

class CatalogItemUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    emoji: Optional[str] = None
    prompt_sugerencia: Optional[str] = None
    activo: Optional[bool] = None

class CatalogItemResponse(CatalogItemBase):
    id: int
    activo: bool
    created_at: datetime
    veces_usado: int
    
    class Config:
        from_attributes = True

# ============= ADMIN SCHEMAS =============

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class AdminUserResponse(BaseModel):
    id: int
    username: str
    email: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# ============= STATS SCHEMAS =============

class StoryStatsResponse(BaseModel):
    total_historias: int
    total_interacciones: int
    historias_por_grupo: dict
    promedio_interacciones: float
    ultimas_historias: List[StoryListResponse]