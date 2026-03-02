from pydantic import BaseModel

class PasswordCreate(BaseModel):
    service: str
    login: str
    password: str  # plaintext z formularza
    key: str  # klucz Fernet do szyfrowania

class PasswordOut(BaseModel):
    id: int
    service: str
    login: str
    password: str  # zwrócimy odszyfrowany tekst (na dev)

    model_config = {"from_attributes": True}
