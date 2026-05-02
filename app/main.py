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

from fastapi.responses import JSONResponse
import logging

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request, call_next):
    print(f"DEBUG: Request {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        print(f"DEBUG: Response {response.status_code}")
        return response
    except Exception as e:
        print(f"ERROR: Exception during request: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal Server Error", "error": str(e)}
        )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc)}
    )

# Inicializar BD al arrancar
@app.on_event("startup")
async def startup_event():
    init_db()
    print("[OK] Base de datos inicializada")

# Incluir routers
app.include_router(stories.router, prefix="/api")
app.include_router(catalog.router, prefix="/api/catalog")
app.include_router(admin.router, prefix="/api/admin")

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