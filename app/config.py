import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:@localhost:3306/cuentacuentos"
    )
    
    # Admin
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    
    # JWT
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas
    
    # App
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Configuración de historias por edad
    AGE_GROUPS = {
        "3-5": {
            "name": "Pequeños Exploradores",
            "color": "#FFB6C1",
            "story_length": 80,
            "vocabulary": "muy simple",
            "interactions": 2
        },
        "6-8": {
            "name": "Aventureros",
            "color": "#87CEEB",
            "story_length": 100,
            "vocabulary": "simple",
            "interactions": 3
        },
        "9-12": {
            "name": "Soñadores",
            "color": "#98FB98",
            "story_length": 120,
            "vocabulary": "moderado",
            "interactions": 4
        }
    }

settings = Settings()