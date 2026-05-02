from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum

class CatalogType(str, enum.Enum):
    PROTAGONISTA = "protagonista"
    LUGAR = "lugar"
    EMOCION = "emocion"

class Story(Base):
    __tablename__ = "stories"
    
    id = Column(Integer, primary_key=True, index=True)
    edad_usuario = Column(Integer, nullable=False)
    grupo_edad = Column(String(10), nullable=False)  # "3-5", "6-8", "9-12"
    
    # Historia completa
    texto_completo = Column(Text, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    duracion_segundos = Column(Integer, nullable=True)  # Duración total de la sesión
    
    # Relaciones
    interacciones = relationship("StoryInteraction", back_populates="story", cascade="all, delete-orphan")

class StoryInteraction(Base):
    __tablename__ = "story_interactions"
    
    id = Column(Integer, primary_key=True, index=True)
    story_id = Column(Integer, ForeignKey("stories.id"), nullable=False)
    
    orden = Column(Integer, nullable=False)  # 0=inicial, 1=primera interacción, etc.
    objeto_dibujado = Column(String(200), nullable=False)
    texto_generado = Column(Text, nullable=False)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relación
    story = relationship("Story", back_populates="interacciones")

class CatalogItem(Base):
    __tablename__ = "catalog_items"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(CatalogType), nullable=False)  # protagonista, lugar, emocion
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(Text, nullable=True)
    emoji = Column(String(10), nullable=True)
    
    # Prompts personalizados para la IA
    prompt_sugerencia = Column(Text, nullable=True)
    
    activo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Estadísticas
    veces_usado = Column(Integer, default=0, server_default="0")

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    email = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)