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
    """Return this user's KDF salt, generating it on first call. Not secret - only PIN + Fernet key are."""
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
    """Store the vault verifier (opaque AES-GCM blob made in the browser). Write-once."""
    if current_user.vault_verifier:
        raise HTTPException(status_code=409, detail="Sejf ma już ustawiony weryfikator")

    current_user.vault_verifier = data.verifier
    db.add(current_user)
    db.commit()
    return {"message": "Verifier saved"}
