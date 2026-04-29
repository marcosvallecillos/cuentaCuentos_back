from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import schemas, crud
from app.database import get_db
from app.services.story_service import story_service
from app.services.ai_service import ai_service

router = APIRouter(prefix="/api/stories", tags=["Stories"])

@router.post("/generate", response_model=schemas.StoryResponse)
async def generar_historia_inicial(
    request: schemas.StoryCreate,
    db: Session = Depends(get_db)
):
    """
    Genera el inicio de una historia y la guarda en BD
    """
    try:
        # Generar historia con IA
        objeto = request.texto_completo.split('\n')[0]  # Simplificado para MVP
        edad = request.edad_usuario
        
        historia_raw = ai_service.generar_historia_inicial(objeto, edad, db)
        resultado = story_service.parsear_historia(historia_raw, edad, 0)
        
        # Guardar en BD
        story_create = schemas.StoryCreate(
            edad_usuario=edad,
            grupo_edad=ai_service.get_age_group(edad),
            texto_completo=resultado.historia,
            duracion_segundos=None
        )
        
        db_story = crud.create_story(db, story_create)
        
        # Guardar primera interacción
        interaction = schemas.StoryInteractionCreate(
            orden=0,
            objeto_dibujado=objeto,
            texto_generado=resultado.historia
        )
        crud.create_story_interaction(db, db_story.id, interaction)
        
        # Convertir a response con interacciones
        response = schemas.StoryResponse.model_validate(db_story)
        response.interacciones = [schemas.StoryInteractionResponse.model_validate(i) for i in db_story.interacciones]
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar historia: {str(e)}")

@router.get("/", response_model=List[schemas.StoryListResponse])
async def listar_historias(
    skip: int = 0,
    limit: int = 50,
    grupo_edad: str = None,
    db: Session = Depends(get_db)
):
    """Listar historias con preview"""
    stories = crud.get_stories(db, skip=skip, limit=limit, grupo_edad=grupo_edad)
    
    result = []
    for story in stories:
        result.append(schemas.StoryListResponse(
            id=story.id,
            edad_usuario=story.edad_usuario,
            grupo_edad=story.grupo_edad,
            preview=story.texto_completo[:100] + "..." if len(story.texto_completo) > 100 else story.texto_completo,
            created_at=story.created_at,
            num_interacciones=len(story.interacciones)
        ))
    
    return result

@router.get("/{story_id}", response_model=schemas.StoryResponse)
async def obtener_historia(story_id: int, db: Session = Depends(get_db)):
    """Obtener historia completa por ID"""
    story = crud.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    
    return schemas.StoryResponse.model_validate(story)

@router.delete("/{story_id}")
async def eliminar_historia(story_id: int, db: Session = Depends(get_db)):
    """Eliminar historia"""
    success = crud.delete_story(db, story_id)
    if not success:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    
    return {"message": "Historia eliminada exitosamente"}

@router.get("/stats/overview", response_model=schemas.StoryStatsResponse)
async def obtener_estadisticas(db: Session = Depends(get_db)):
    """Obtener estadísticas generales"""
    stats = crud.get_story_stats(db)
    ultimas = crud.get_stories(db, limit=5)
    
    ultimas_list = []
    for story in ultimas:
        ultimas_list.append(schemas.StoryListResponse(
            id=story.id,
            edad_usuario=story.edad_usuario,
            grupo_edad=story.grupo_edad,
            preview=story.texto_completo[:100] + "...",
            created_at=story.created_at,
            num_interacciones=len(story.interacciones)
        ))
    
    return schemas.StoryStatsResponse(
        **stats,
        ultimas_historias=ultimas_list
    )