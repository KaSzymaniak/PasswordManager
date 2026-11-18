import os
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
import jwt
import bcrypt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db

load_dotenv()

logger = logging.getLogger("uvicorn.error")

# ========== JWT (autentykacja użytkowników) ==========
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    # Brak klucza w .env - losowy klucz na czas działania procesu. Bezpieczny
    # (nikt go nie zna), ale po restarcie serwera wszystkie sesje wygasają.
    SECRET_KEY = secrets.token_urlsafe(32)
    logger.warning("SECRET_KEY nie jest ustawiony w .env - użyto losowego klucza, "
                   "sesje wygasną po restarcie serwera")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def hash_password(password: str) -> str:
    """Hashuje hasło algorytmem bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Sprawdza hasło z hashem bcrypt."""
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Tworzy podpisany token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_token_from_request(request: Request) -> str:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1].strip()

    cookie_token = request.cookies.get("access_token", "")
    if cookie_token:
        return cookie_token.strip()

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Brak autoryzacji",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
):
    """Weryfikuje token JWT i zwraca zalogowanego użytkownika."""
    from app.models.user import User

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowy lub wygasły token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = get_token_from_request(request)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credential_exception
    except jwt.InvalidTokenError:
        raise credential_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credential_exception
    return user
