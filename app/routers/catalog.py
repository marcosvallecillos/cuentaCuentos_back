from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud, models
from app.database import get_db

router = APIRouter(prefix="/api/catalog", tags=["Catalog"])

@router.post("/", response_model=schemas.CatalogItemResponse)
async def crear_item(
    item: schemas.CatalogItemCreate,
    db: Session = Depends(get_db)
):
    """Crear nuevo item en el catálogo"""
    try:
        db_item = crud.create_catalog_item(db, item)
        return schemas.CatalogItemResponse.model_validate(db_item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[schemas.CatalogItemResponse])
async def listar_items(
    tipo: Optional[models.CatalogType] = None,
    activo: bool = True,
    db: Session = Depends(get_db)
):
    """Listar items del catálogo"""
    items = crud.get_catalog_items(db, tipo=tipo, activo=activo)
    return [schemas.CatalogItemResponse.model_validate(item) for item in items]

@router.get("/{item_id}", response_model=schemas.CatalogItemResponse)
async def obtener_item(item_id: int, db: Session = Depends(get_db)):
    """Obtener item por ID"""
    item = crud.get_catalog_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return schemas.CatalogItemResponse.model_validate(item)

@router.put("/{item_id}", response_model=schemas.CatalogItemResponse)
async def actualizar_item(
    item_id: int,
    item_update: schemas.CatalogItemUpdate,
    db: Session = Depends(get_db)
):
    """Actualizar item del catálogo"""
    updated = crud.update_catalog_item(db, item_id, item_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return schemas.CatalogItemResponse.model_validate(updated)

@router.delete("/{item_id}")
async def eliminar_item(item_id: int, db: Session = Depends(get_db)):
    """Eliminar item del catálogo"""
    success = crud.delete_catalog_item(db, item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return {"message": "Item eliminado exitosamente"}