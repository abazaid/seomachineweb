from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.db import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin, UserOut


router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)):
    if payload.role not in {'admin', 'manager', 'writer'}:
        raise HTTPException(status_code=400, detail='Role must be admin, manager, or writer')

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already exists')

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post('/login', response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid email or password')

    token = create_access_token(subject=user.email, role=user.role)
    return TokenResponse(access_token=token, user=user)


@router.get('/me', response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
