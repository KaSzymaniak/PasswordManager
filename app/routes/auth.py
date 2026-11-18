import secrets
from datetime import timedelta, datetime
import os
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserOut,
    EmailVerifyRequest,
    ResendVerificationRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_user,
)
from app.email_utils import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["auth"])


def _generate_code() -> str:
    """Generuje jednorazowy 6-cyfrowy kod."""
    return f"{secrets.randbelow(1_000_000):06d}"


@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Rejestracja nowego użytkownika."""
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ten adres email jest już zarejestrowany"
        )
    
    # Konto pozostaje niezweryfikowane do czasu potwierdzenia kodu z emaila
    hashed_password = hash_password(user.password)
    code = _generate_code()
    new_user = User(
        email=user.email,
        hashed_password=hashed_password,
        email_verified=False,
        email_verification_code=code,
        email_verification_expires=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    send_verification_email(new_user.email, code)

    return new_user


@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Logowanie - ustawia token JWT w ciasteczku HttpOnly."""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło"
        )
    
    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nieprawidłowy email lub hasło"
        )

    if not db_user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Przed zalogowaniem potwierdź adres email"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    
    is_secure_cookie = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_secure_cookie,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {"message": "Zalogowano"}


@router.post("/logout")
def logout(response: Response):
    """Wylogowanie - usuwa ciasteczko z tokenem."""
    response.delete_cookie(key="access_token", path="/")
    return {"message": "Wylogowano"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """Dane zalogowanego użytkownika."""
    return current_user


@router.post("/verify-email")
def verify_email(payload: EmailVerifyRequest, db: Session = Depends(get_db)):
    """Potwierdza adres email kodem wysłanym przy rejestracji."""
    db_user = db.query(User).filter(User.email == payload.email).first()

    invalid = (
        not db_user
        or not db_user.email_verification_code
        or db_user.email_verification_code != payload.code
        or db_user.email_verification_expires is None
        or db_user.email_verification_expires < datetime.utcnow()
    )
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy lub wygasły kod weryfikacyjny"
        )

    db_user.email_verified = True
    db_user.email_verification_code = None
    db_user.email_verification_expires = None
    db.commit()

    return {"message": "Adres email potwierdzony"}


@router.post("/resend-verification")
def resend_verification(payload: ResendVerificationRequest, db: Session = Depends(get_db)):
    """Generuje nowy kod weryfikacyjny, unieważniając poprzedni."""
    db_user = db.query(User).filter(User.email == payload.email).first()

    if db_user and not db_user.email_verified:
        code = _generate_code()
        db_user.email_verification_code = code
        db_user.email_verification_expires = datetime.utcnow() + timedelta(hours=24)
        db.commit()
        send_verification_email(db_user.email, code)

    return {"message": "Jeśli konto istnieje i nie jest zweryfikowane, wysłano nowy kod"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Wysyła kod resetu hasła; odpowiedź jest identyczna niezależnie od istnienia konta."""
    db_user = db.query(User).filter(User.email == payload.email).first()

    if db_user:
        code = _generate_code()
        db_user.password_reset_code = code
        db_user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        send_password_reset_email(db_user.email, code)

    return {"message": "Jeśli konto z tym adresem istnieje, wysłano kod resetu hasła"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Ustawia nowe hasło na podstawie kodu z /forgot-password."""
    db_user = db.query(User).filter(User.email == payload.email).first()

    invalid = (
        not db_user
        or not db_user.password_reset_code
        or db_user.password_reset_code != payload.code
        or db_user.password_reset_expires is None
        or db_user.password_reset_expires < datetime.utcnow()
    )
    if invalid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nieprawidłowy lub wygasły kod resetu"
        )

    db_user.hashed_password = hash_password(payload.new_password)
    db_user.password_reset_code = None
    db_user.password_reset_expires = None
    db.commit()

    return {"message": "Hasło zostało zmienione"}
