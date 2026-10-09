from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import jwt

from app.database import get_db
from app.models import User
from app.schemas.auth import SignUpRequest, LoginRequest, UserResponse
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_id_from_token,
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
bearer_scheme = HTTPBearer()


@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(data: SignUpRequest, db: Session = Depends(get_db)):
    email = str(data.email).lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=email, password_hash=hash_password(data.password))
    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    return user


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = str(data.email).lower().strip()
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    return {"access_token": create_access_token(user.id), "token_type": "bearer"}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        user_id = get_user_id_from_token(credentials.credentials)
    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    return user


@router.get("/me", response_model=UserResponse)
def read_current_user(user: User = Depends(get_current_user)):
    return user