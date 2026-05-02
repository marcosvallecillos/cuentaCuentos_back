from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud
from app.database import get_db
from app.services.story_service import story_service
from app.services.ai_service import ai_service
from pydantic import BaseModel

router = APIRouter(tags=["Stories"])

# ============= SCHEMAS COMPATIBLES CON FRONTEND ORIGINAL =============

class GenerarHistoriaRequest(BaseModel):
    objeto: str
    edad: int

class ContinuarHistoriaRequest(BaseModel):
    historia_actual: str
    nuevo_objeto: str
    edad: int
    interaccion_numero: int

class StoryResponseFrontend(BaseModel):
    historia: str
    audio_text: str
    necesita_interaccion: bool
    prompt_interaccion: Optional[str] = None
    opciones: List[str] = []
    progreso: dict

# ============= ENDPOINTS PARA APP PRINCIPAL =============

@router.post("/generar-historia", response_model=StoryResponseFrontend)
async def generar_historia(
    request: GenerarHistoriaRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para la app principal (niños)
    Genera historia inicial basada en el dibujo
    """
    try:
        if not request.objeto or request.objeto.strip() == "":
            raise HTTPException(status_code=400, detail="Debes especificar un objeto o personaje")
        
        print(f"=== Generando historia inicial ===")
        print(f"Objeto: {request.objeto}")
        print(f"Edad: {request.edad}")
        
        # Generar con IA (adaptado a la firma original)
        historia_raw = ai_service.generar_historia_inicial(
            objeto=request.objeto,
            edad=request.edad,
            db=db
        )
        
        print(f"Historia raw generada: {len(historia_raw)} caracteres")
        
        # Parsear
        resultado = story_service.parsear_historia(historia_raw, request.edad, 0)
        
        print(f"[OK] Historia parseada exitosamente")
        print(f"Necesita interacción: {resultado.necesita_interaccion}")
        
        # Guardar en BD
        try:
            grupo_edad = ai_service.get_age_group(request.edad)
            
            story_create = schemas.StoryCreate(
                edad_usuario=request.edad,
                grupo_edad=grupo_edad,
                texto_completo=resultado.historia,
                duracion_segundos=None
            )
            
            db_story = crud.create_story(db, story_create)
            print(f"[OK] Historia guardada con ID: {db_story.id}")
            
            # Guardar primera interacción
            interaction = schemas.StoryInteractionCreate(
                orden=0,
                objeto_dibujado=request.objeto,
                texto_generado=resultado.historia
            )
            crud.create_story_interaction(db, db_story.id, interaction)
            print(f"[OK] Interacción guardada")
            
        except Exception as db_error:
            print(f"[WARN] Error guardando en BD (continuamos): {db_error}")
            import traceback
            traceback.print_exc()
        
        # Retornar respuesta compatible con frontend
        return StoryResponseFrontend(
            historia=resultado.historia,
            audio_text=resultado.audio_text,
            necesita_interaccion=resultado.necesita_interaccion,
            prompt_interaccion=resultado.prompt_interaccion,
            opciones=resultado.opciones,
            progreso=resultado.progreso
        )
        
    except Exception as e:
        print(f"[ERROR] ERROR FATAL en generar_historia: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al generar historia: {str(e)}")


@router.post("/continuar-historia", response_model=StoryResponseFrontend)
async def continuar_historia(
    request: ContinuarHistoriaRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para continuar la historia con nuevo dibujo
    """
    try:
        if not request.nuevo_objeto or request.nuevo_objeto.strip() == "":
            raise HTTPException(status_code=400, detail="Debes especificar el nuevo objeto")
        
        print(f"=== Continuando historia ===")
        print(f"Nuevo objeto: {request.nuevo_objeto}")
        print(f"Interacción #: {request.interaccion_numero}")
        
        # Continuar con IA
        continuacion_raw = ai_service.continuar_historia(
            historia_actual=request.historia_actual,
            nuevo_objeto=request.nuevo_objeto,
            edad=request.edad,
            interaccion_numero=request.interaccion_numero,
            db=db
        )
        
        print(f"Continuación generada: {len(continuacion_raw)} caracteres")
        
        # Parsear
        resultado = story_service.parsear_historia(
            continuacion_raw, 
            request.edad, 
            request.interaccion_numero
        )
        
        print(f"[OK] Continuación parseada")
        
        return StoryResponseFrontend(
            historia=resultado.historia,
            audio_text=resultado.audio_text,
            necesita_interaccion=resultado.necesita_interaccion,
            prompt_interaccion=resultado.prompt_interaccion,
            opciones=resultado.opciones,
            progreso=resultado.progreso
        )
        
    except Exception as e:
        print(f"[ERROR] ERROR FATAL en continuar_historia: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error al continuar historia: {str(e)}")


# ============= ENDPOINTS ADMIN (Panel) =============

@router.get("/stories/", response_model=List[schemas.StoryListResponse])
async def listar_historias(
    skip: int = 0,
    limit: int = 50,
    grupo_edad: str = None,
    db: Session = Depends(get_db)
):
    """Listar historias (panel admin)"""
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


@router.get("/stories/{story_id}", response_model=schemas.StoryResponse)
async def obtener_historia(story_id: int, db: Session = Depends(get_db)):
    """Obtener historia completa por ID"""
    story = crud.get_story(db, story_id)
    if not story:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    
    return schemas.StoryResponse.model_validate(story)


@router.delete("/stories/{story_id}")
async def eliminar_historia(story_id: int, db: Session = Depends(get_db)):
    """Eliminar historia"""
    success = crud.delete_story(db, story_id)
    if not success:
        raise HTTPException(status_code=404, detail="Historia no encontrada")
    
    return {"message": "Historia eliminada exitosamente"}


@router.get("/stories/stats/overview", response_model=schemas.StoryStatsResponse)
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