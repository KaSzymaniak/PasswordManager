from fastapi import APIRouter, Depends, HTTPException, Body, status
from sqlalchemy.orm import Session
import hashlib
from app.database import get_db
from app.models.password import PasswordEntry
from app.models.user import User
from app.schemas.password import PasswordCreate, PasswordOut
from app.security import encrypt_text, decrypt_text, get_current_user
from cryptography.fernet import Fernet, InvalidToken

router = APIRouter(prefix="/passwords", tags=["passwords"])


def get_user_passwords(user_id: int, db: Session):
    """Helper to get only current user's passwords"""
    return db.query(PasswordEntry).filter(PasswordEntry.user_id == user_id).all()


def _hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


def ensure_user_fernet_key(current_user: User, key: str, db: Session):
    """Bind Fernet key to user on first use; reject different keys afterwards."""
    key_hash = _hash_key(key)

    if not current_user.fernet_key_hash:
        current_user.fernet_key_hash = key_hash
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        return

    if current_user.fernet_key_hash != key_hash:
        raise HTTPException(
            status_code=403,
            detail="Ten klucz Fernet nie jest przypisany do tego konta",
        )


# 🔹 Pobierz wszystkie hasła użytkownika (domyślnie zaszyfrowane)
@router.get("", response_model=list[PasswordOut])
def get_passwords(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = get_user_passwords(current_user.id, db)
    return [
        PasswordOut(
            id=it.id,
            service=it.service,
            login=it.login,
            password=it.password  # zwracamy ZASZYFROWANE
        )
        for it in items
    ]


# 🔹 Dodaj nowe hasło
@router.post("", response_model=PasswordOut)
def add_password(
    password: PasswordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not password.key or not password.key.strip():
        raise HTTPException(status_code=400, detail="Brak klucza Fernet")
    
    key_used = password.key.strip()
    ensure_user_fernet_key(current_user, key_used, db)
    
    try:
        encrypted_password = encrypt_text(password.password, key_used)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd szyfrowania: {str(e)}")
    
    new_entry = PasswordEntry(
        user_id=current_user.id,
        service=password.service,
        login=password.login,
        password=encrypted_password
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return PasswordOut(
        id=new_entry.id,
        service=new_entry.service,
        login=new_entry.login,
        password=new_entry.password
    )


# 🔹 Edytuj hasło
@router.put("/{password_id}", response_model=PasswordOut)
def update_password(
    password_id: int,
    updated: PasswordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(PasswordEntry).filter(
        PasswordEntry.id == password_id,
        PasswordEntry.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(status_code=404, detail="Hasło nie istnieje")

    if not updated.key or not updated.key.strip():
        raise HTTPException(status_code=400, detail="Brak klucza Fernet")

    ensure_user_fernet_key(current_user, updated.key.strip(), db)
    
    try:
        item.service = updated.service
        item.login = updated.login
        item.password = encrypt_text(updated.password, updated.key.strip())
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd szyfrowania: {str(e)}")

    db.commit()
    db.refresh(item)

    return PasswordOut(
        id=item.id,
        service=item.service,
        login=item.login,
        password=item.password
    )


# 🔹 Usuń hasło
@router.delete("/{password_id}")
def delete_password(
    password_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    entry = db.query(PasswordEntry).filter(
        PasswordEntry.id == password_id,
        PasswordEntry.user_id == current_user.id
    ).first()
    
    if not entry:
        raise HTTPException(status_code=404, detail="Hasło nie znalezione")
    
    db.delete(entry)
    db.commit()
    return {"message": "Password deleted"}


# 🔹 Odszyfruj hasło (ręcznie - użytkownik podaje klucz Fernet)
@router.post("/decrypt", response_model=dict)
def decrypt_via_key(
    payload: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    key = (payload.get("key") or "").strip()
    encrypted = (payload.get("password") or "").strip()
    
    if not key or not encrypted:
        raise HTTPException(status_code=400, detail="Brak klucza lub hasła")

    ensure_user_fernet_key(current_user, key, db)

    # Walidacja formatu klucza
    try:
        f = Fernet(key.encode())
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Zły format klucza Fernet (musi być 44 znaki base64)"
        )

    # Próba odszyfrowania
    try:
        plain = f.decrypt(encrypted.encode()).decode()
        return {"decrypted": plain}
    except InvalidToken:
        raise HTTPException(status_code=400, detail="Nieprawidłowy klucz - nie pasuje do tego hasła")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Błąd odszyfrowania: {str(e)}")
