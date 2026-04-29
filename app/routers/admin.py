from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app import schemas, crud, models
from app.database import get_db
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["Admin"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verificar token JWT"""
    try:
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado"
        )

@router.post("/login", response_model=schemas.AdminTokenResponse)
async def login(
    request: schemas.AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """Login de administrador"""
    # Verificar si existe el usuario
    admin = crud.get_admin_by_username(db, request.username)
    
    # Si no existe, crear el usuario por defecto en primera ejecución
    if not admin and request.username == settings.ADMIN_USERNAME:
        hashed_pw = get_password_hash(settings.ADMIN_PASSWORD)
        admin = crud.create_admin_user(db, settings.ADMIN_USERNAME, hashed_pw)
    
    if not admin or not verify_password(request.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario desactivado"
        )
    
    # Actualizar último login
    crud.update_last_login(db, admin.id)
    
    # Crear token
    access_token = create_access_token(data={"sub": admin.username})
    
    return schemas.AdminTokenResponse(access_token=access_token)

@router.get("/verify")
async def verify_admin(username: str = Depends(verify_token)):
    """Verificar si el token es válido"""
    return {"username": username, "valid": True}

@router.get("/me", response_model=schemas.AdminUserResponse)
async def get_current_admin(
    username: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Obtener información del admin actual"""
    admin = crud.get_admin_by_username(db, username)
    if not admin:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    return schemas.AdminUserResponse.model_validate(admin)