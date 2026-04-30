from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.routers import stories, catalog, admin
from app.config import settings
from app.database import init_db

app = FastAPI(
    title="Drawn Worlds API",
    description="API para generación de cuentos interactivos infantiles con panel admin",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar BD al arrancar
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Base de datos inicializada")

# Incluir routers
app.include_router(stories.router)
app.include_router(catalog.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {
        "mensaje": "Drawn Worlds API v2.0",
        "version": "2.0.0",
        "status": "activo",
        "features": [
            "Generación de historias con IA",
            "Panel de administración",
            "Catálogo de elementos",
            "Historial completo"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "database": "connected"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)