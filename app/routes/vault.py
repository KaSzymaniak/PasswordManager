import secrets
import base64
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.security import get_current_user

router = APIRouter(prefix="/vault", tags=["vault"])


class VerifierIn(BaseModel):
    verifier: str


@router.get("/salt")
def get_salt(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Zwraca sól KDF użytkownika (generowaną przy pierwszym wywołaniu). Sól nie jest tajna - tajne są tylko PIN i klucz sejfu."""
    is_new = not current_user.kdf_salt
    if is_new:
        current_user.kdf_salt = base64.b64encode(secrets.token_bytes(16)).decode()
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

    return {"salt": current_user.kdf_salt, "is_new": is_new, "verifier": current_user.vault_verifier}


@router.put("/verifier")
def set_verifier(
    data: VerifierIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Zapisuje weryfikator sejfu (szyfrogram AES-GCM utworzony w przeglądarce). Zapis jednorazowy."""
    if current_user.vault_verifier:
        raise HTTPException(status_code=409, detail="Sejf ma już ustawiony weryfikator")

    current_user.vault_verifier = data.verifier
    db.add(current_user)
    db.commit()
    return {"message": "Weryfikator zapisany"}
