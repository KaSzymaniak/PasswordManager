# Menedżer Haseł - Dokumentacja Architektury

Dokument opisuje **aktualny stan** systemu. Historia zmian znajduje się w
`docs/CHANGELOG.md`.

## Przegląd systemu

Menedżer Haseł to aplikacja webowa do bezpiecznego przechowywania i
zarządzania hasłami, z szyfrowaniem end-to-end wykonywanym w całości w
przeglądarce (model zero-knowledge - serwer nigdy nie widzi PIN-u, klucza
sejfu ani hasła w postaci jawnej).

### Technologie
- **Backend**: FastAPI (Python 3.13+)
- **Frontend**: Vue 3 + Vite
- **Baza danych**: SQLite
- **Szyfrowanie**: Web Crypto API w przeglądarce - PBKDF2-HMAC-SHA256
  (310 000 iteracji) z PIN + klucz sejfu + sól konta → AES-256-GCM.
  Backend nie wykonuje żadnej kryptografii haseł, przechowuje wyłącznie
  gotowy szyfrogram.
- **Autentykacja**: JWT w ciasteczku HttpOnly

---

## Model bezpieczeństwa - dwie niezależne warstwy

- **Konto** (kto się loguje): email + hasło, weryfikacja emailem po
  rejestracji, reset hasła kodem wysłanym mailem. Odzyskiwalne.
- **Sejf** (co odszyfrowuje hasła): PIN + klucz sejfu + sól. PIN i klucz
  istnieją tylko w pamięci sesji przeglądarki, nigdy nie są zapisywane ani
  wysyłane do serwera. Nieodzyskiwalne z założenia (zero-knowledge).

Pełny model zagrożeń i uzasadnienie: `docs/RECOVERY.md`.

### Weryfikator sejfu

Przy pierwszym odblokowaniu przeglądarka szyfruje kluczem szyfrującym znaną stałą
i zapisuje wynik na serwerze (`PUT /vault/verifier`). Przy kolejnych
odblokowaniach przeglądarka próbuje go odszyfrować - niepowodzenie oznacza
błędną kombinację PIN + klucz sejfu. Dzięki temu błędna kombinacja jest
odrzucana, zanim zostanie użyta do zaszyfrowania nowego hasła.

Weryfikator sprawdza PIN i klucz sejfu **łącznie**. Nie da się nim
zweryfikować samego PIN-u, więc nie umożliwia zgadywania PIN-u
(10 000 kombinacji dla 4 cyfr) niezależnie od klucza sejfu. Z tego samego
powodu komunikat błędu nie rozróżnia złego PIN-u od złego klucza.

---

## Architektura aplikacji

### Backend
```
app/
├── main.py              # Aplikacja FastAPI, CORS, nagłówki bezpieczeństwa
├── database.py          # Konfiguracja SQLAlchemy, migracja kolumn (ALTER TABLE)
├── security.py          # JWT, hashowanie haseł (bcrypt)
├── email_utils.py       # Wysyłka kodów mailem (SMTP) lub do logu serwera
├── models/
│   ├── user.py          # Model User
│   └── password.py      # Model PasswordEntry
├── routes/
│   ├── auth.py          # Endpointy /auth/*
│   ├── password.py      # Endpointy /passwords/*
│   └── vault.py         # Endpointy /vault/* (sól KDF, weryfikator)
└── schemas/
    ├── user.py
    └── password.py
```

### Frontend
```
frontend/frontend-app/
├── src/
│   ├── App.vue          # Główny komponent (Options API, bez routera)
│   ├── crypto.js        # PBKDF2 + AES-GCM (Web Crypto API)
│   ├── main.js
│   └── style.css
├── dist/                # Build produkcyjny (serwowany przez backend)
└── vite.config.js
```

### Schemat bazy danych

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,                -- bcrypt
    email_verified BOOLEAN DEFAULT 0,
    email_verification_code VARCHAR,
    email_verification_expires DATETIME,
    password_reset_code VARCHAR,
    password_reset_expires DATETIME,
    kdf_salt VARCHAR,                       -- sól PBKDF2 (base64, 16 bajtów)
    vault_verifier VARCHAR                  -- weryfikator sejfu: base64(IV || AES-GCM)
);

CREATE TABLE passwords (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    service VARCHAR,
    login VARCHAR,
    password VARCHAR,                       -- szyfrogram: base64(IV || AES-GCM)
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## Endpointy API

### Autentykacja (`/auth`)
- `POST /auth/register` - rejestracja (konto tworzone jako niezweryfikowane)
- `POST /auth/login` - logowanie (ustawia ciasteczko HttpOnly), odrzuca
  niezweryfikowane konta (403)
- `POST /auth/logout` - wylogowanie (usuwa ciasteczko)
- `GET /auth/me` - dane zalogowanego użytkownika
- `POST /auth/verify-email` - potwierdzenie kodu wysłanego przy rejestracji
- `POST /auth/resend-verification` - nowy kod weryfikacyjny
- `POST /auth/forgot-password` - wysyła kod resetu (identyczna odpowiedź
  niezależnie od istnienia konta - ochrona przed enumeracją)
- `POST /auth/reset-password` - ustawia nowe hasło kodem z maila

### Sejf (`/vault`)
- `GET /vault/salt` - zwraca (przy pierwszym wywołaniu generuje) sól KDF
  oraz weryfikator sejfu zalogowanego użytkownika
- `PUT /vault/verifier` - zapisuje weryfikator sejfu (jednorazowo; ponowny
  zapis zwraca 409)

### Hasła (`/passwords`)
- `GET /passwords` - lista haseł (szyfrogramy, odszyfrowanie w przeglądarce)
- `POST /passwords` - dodanie hasła (szyfrogram przygotowany w przeglądarce)
- `PUT /passwords/{id}` - edycja hasła
- `DELETE /passwords/{id}` - usunięcie hasła

---

## Wdrożenie

### Środowisko deweloperskie
```bash
# Backend (z katalogu głównego)
python -m uvicorn app.main:app --reload --reload-dir app

# Build frontendu
cd frontend/frontend-app
npm run build
```
