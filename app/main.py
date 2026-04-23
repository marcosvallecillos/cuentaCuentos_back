
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import StoryRequest, ContinueStoryRequest, StoryResponse
from app.services.story_service import story_service
from app.config import settings

app = FastAPI(
    title="Drawn Worlds API",
    description="API para generación de cuentos interactivos infantiles",
    version="1.0.0"
)

# CORS para Angular
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "mensaje": "Drawn Worlds API",
        "version": "1.0.0",
        "status": "activo"
    }

@app.post("/api/generar-historia", response_model=StoryResponse)
async def generar_historia(request: StoryRequest):
    """
    Genera el inicio de una historia basada en las selecciones iniciales
    """
    try:
        resultado = story_service.crear_historia_inicial(
            personaje=request.personaje,
            lugar=request.lugar,
            emocion=request.emocion,
            edad=request.edad
        )
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar historia: {str(e)}")

@app.post("/api/continuar-historia", response_model=StoryResponse)
async def continuar_historia(request: ContinueStoryRequest):
    """
    Continúa la historia incorporando un nuevo personaje elegido
    """
    try:
        resultado = story_service.continuar_historia(
            historia_actual=request.historia_actual,
            nuevo_personaje=request.nuevo_objeto, # Reutilizamos campo o actualizamos modelo
            edad=request.edad,
            interaccion_numero=request.interaccion_numero
        )
        
        return resultado
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al continuar historia: {str(e)}")

@app.get("/api/grupos-edad")
async def obtener_grupos_edad():
    """
    Retorna la configuración de grupos de edad
    """
    return settings.AGE_GROUPS

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)