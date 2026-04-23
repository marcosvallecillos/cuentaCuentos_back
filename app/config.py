import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
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