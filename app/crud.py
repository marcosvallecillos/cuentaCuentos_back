from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from app import models, schemas
from datetime import datetime, timedelta

# ============= STORIES CRUD =============

def create_story(db: Session, story: schemas.StoryCreate) -> models.Story:
    """Crear nueva historia"""
    db_story = models.Story(**story.model_dump())
    db.add(db_story)
    db.commit()
    db.refresh(db_story)
    return db_story

def create_story_interaction(
    db: Session, 
    story_id: int, 
    interaction: schemas.StoryInteractionCreate
) -> models.StoryInteraction:
    """Crear interacción de historia"""
    db_interaction = models.StoryInteraction(
        story_id=story_id,
        **interaction.model_dump()
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction

def get_story(db: Session, story_id: int) -> Optional[models.Story]:
    """Obtener historia por ID"""
    return db.query(models.Story).filter(models.Story.id == story_id).first()

def get_stories(
    db: Session, 
    skip: int = 0, 
    limit: int = 50,
    grupo_edad: Optional[str] = None
) -> List[models.Story]:
    """Listar historias con filtros"""
    query = db.query(models.Story)
    
    if grupo_edad:
        query = query.filter(models.Story.grupo_edad == grupo_edad)
    
    return query.order_by(desc(models.Story.created_at)).offset(skip).limit(limit).all()

def delete_story(db: Session, story_id: int) -> bool:
    """Eliminar historia"""
    story = db.query(models.Story).filter(models.Story.id == story_id).first()
    if story:
        db.delete(story)
        db.commit()
        return True
    return False

def get_story_stats(db: Session) -> dict:
    """Obtener estadísticas de historias"""
    total = db.query(func.count(models.Story.id)).scalar()
    total_interacciones = db.query(func.count(models.StoryInteraction.id)).scalar()
    
    # Historias por grupo
    grupos = db.query(
        models.Story.grupo_edad,
        func.count(models.Story.id).label('count')
    ).group_by(models.Story.grupo_edad).all()
    
    historias_por_grupo = {grupo: count for grupo, count in grupos}
    
    # Promedio de interacciones
    avg = db.query(func.avg(
        db.query(func.count(models.StoryInteraction.id))
        .filter(models.StoryInteraction.story_id == models.Story.id)
        .correlate(models.Story)
        .scalar_subquery()
    )).scalar() or 0
    
    return {
        "total_historias": total,
        "total_interacciones": total_interacciones,
        "historias_por_grupo": historias_por_grupo,
        "promedio_interacciones": float(avg)
    }

# ============= CATALOG CRUD =============

def create_catalog_item(db: Session, item: schemas.CatalogItemCreate) -> models.CatalogItem:
    """Crear item de catálogo"""
    db_item = models.CatalogItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_catalog_items(
    db: Session, 
    tipo: Optional[models.CatalogType] = None,
    activo: bool = True
) -> List[models.CatalogItem]:
    """Listar items de catálogo"""
    query = db.query(models.CatalogItem)
    
    if tipo:
        query = query.filter(models.CatalogItem.tipo == tipo)
    
    if activo:
        query = query.filter(models.CatalogItem.activo == True)
    
    return query.order_by(models.CatalogItem.nombre).all()

def get_catalog_item(db: Session, item_id: int) -> Optional[models.CatalogItem]:
    """Obtener item por ID"""
    return db.query(models.CatalogItem).filter(models.CatalogItem.id == item_id).first()

def update_catalog_item(
    db: Session, 
    item_id: int, 
    item_update: schemas.CatalogItemUpdate
) -> Optional[models.CatalogItem]:
    """Actualizar item de catálogo"""
    db_item = get_catalog_item(db, item_id)
    if not db_item:
        return None
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_catalog_item(db: Session, item_id: int) -> bool:
    """Eliminar item de catálogo"""
    item = get_catalog_item(db, item_id)
    if item:
        db.delete(item)
        db.commit()
        return True
    return False

def increment_catalog_usage(db: Session, item_nombre: str):
    """Incrementar contador de uso"""
    item = db.query(models.CatalogItem).filter(
        models.CatalogItem.nombre == item_nombre
    ).first()
    
    if item:
        item.veces_usado += 1
        db.commit()

# ============= ADMIN CRUD =============

def get_admin_by_username(db: Session, username: str) -> Optional[models.AdminUser]:
    """Obtener admin por username"""
    return db.query(models.AdminUser).filter(models.AdminUser.username == username).first()

def create_admin_user(db: Session, username: str, hashed_password: str, email: Optional[str] = None):
    """Crear usuario admin"""
    db_admin = models.AdminUser(
        username=username,
        hashed_password=hashed_password,
        email=email
    )
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin

def update_last_login(db: Session, admin_id: int):
    """Actualizar último login"""
    admin = db.query(models.AdminUser).filter(models.AdminUser.id == admin_id).first()
    if admin:
        admin.last_login = datetime.utcnow()
        db.commit()