from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
from app import schemas, crud, models
from app.database import get_db

router = APIRouter(tags=["Consentimiento"])

@router.post("/consentimiento-parental")
def registrar_consentimiento_parental(
    consent_data: dict,
    request: Request,
    db: Session = Depends(get_db)
):
    # Validar todos aceptados
    if not all([consent_data.get("consent_parental"),
               consent_data.get("aceptacion_privacidad"),
               consent_data.get("aceptacion_tratamiento")]):
        raise HTTPException(status_code=400)
    
    # Crear registro único
    consent_id = str(uuid.uuid4())
    nuevo = models.ConsentimientoParental(
        consent_id=consent_id,
        consent_parental=True,
        aceptacion_privacidad=True,
        aceptacion_tratamiento=True,
        timestamp=datetime.utcnow(),
        ip_origen=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )
    db.add(nuevo)
    db.commit()
    
    return {"consent_id": consent_id, "timestamp": nuevo.timestamp}