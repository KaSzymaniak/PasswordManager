# Password Manager - Dokumentacja Architektury

## Przegląd Systemu

Password Manager to aplikacja webowa do bezpiecznego przechowywania i zarządzania hasłami z szyfrowaniem end-to-end.

### Technologie
- **Backend**: FastAPI (Python 3.13+)
- **Frontend**: Vue 3 + Vite
- **Baza danych**: SQLite
- **Szyfrowanie**: Fernet (cryptography)
- **Autentykacja**: JWT w HttpOnly cookies

---

## Funkcjonalności Bezpieczeństwa

### ✅ Segment 1: Cookie-based Authentication + CORS Hardening

**Implementacja:** Marzec 2026

**Zmiany:**

1. **HttpOnly Cookies dla JWT**
   - Tokeny JWT przechowywane w HttpOnly cookies zamiast localStorage
   - Eliminuje ryzyko XSS - JavaScript nie ma dostępu do tokenów
   - Cookies z flagami: `httponly=True`, `samesite=lax`, `secure` (produkcja)
   
2. **Dual Token Support**
   - Backend akceptuje tokeny z cookies LUB nagłówka Authorization
   - Fallback dla kompatybilności z różnymi klientami
   
3. **CORS Hardening**
   - Ograniczone origins: tylko `localhost:8000`, `127.0.0.1:8000`
   - `credentials=True` - wymagane dla cookies
   - Frontend: `axios.defaults.withCredentials = true`

4. **Auto-login przy odświeżeniu**
   - Endpoint `/auth/me` weryfikuje ważność tokenu
   - Frontend automatycznie loguje użytkownika jeśli cookie jest ważny

**Pliki zmodyfikowane:**
- `app/security.py` - funkcja `get_token_from_request()`
- `app/routes/auth.py` - endpointy login/logout
- `app/main.py` - konfiguracja CORS
- `frontend/frontend-app/src/App.vue` - usunięcie localStorage JWT

---

### ✅ Segment 2: Security Headers + CSP

**Implementacja:** Marzec 2026

**Zmiany:**

1. **Security Headers Middleware**
   - `X-Content-Type-Options: nosniff` - zapobiega MIME type sniffing
   - `X-Frame-Options: DENY` - blokuje clickjacking
   - `Referrer-Policy: no-referrer` - chroni prywatność
   - `Permissions-Policy` - restrykcje API przeglądarki

2. **Content Security Policy (CSP)**
   ```
   default-src 'self';
   script-src 'self' 'unsafe-inline';
   style-src 'self' 'unsafe-inline';
   img-src 'self' data:;
   font-src 'self';
   connect-src 'self';
   frame-ancestors 'none'
   ```

**Pliki zmodyfikowane:**
- `app/main.py` - middleware `security_headers_middleware()`

---

### ✅ UX Improvements: Password Management

**Implementacja:** Marzec 2026

**Zmiany:**

1. **Show/Hide Password Toggle**
   - Przycisk "Pokaż" zmienia się na "Ukryj" po odszyfrowaniu
   - Kliknięcie "Ukryj" chowa hasło bez ponownego wywołania API
   - Reaktywna zmiana tekstu przycisku: `{{ decrypted[item.id] ? 'Ukryj' : 'Pokaż' }}`

2. **Per-User Fernet Key Storage**
   - Każdy użytkownik ma izolowany klucz w localStorage
   - Format: `fernetKey_{email}`
   - Klucz zachowany po wylogowaniu i odświeżeniu strony
   - Automatyczne wczytanie klucza przy logowaniu

3. **Clean State Management**
   - Pole klucza puste przy rejestracji nowego konta
   - Klucz czyszczony z pamięci przy wylogowaniu
   - Brak crossover kluczy między kontami

**Pliki zmodyfikowane:**
- `frontend/frontend-app/src/App.vue`:
  - `togglePasswordVisibility()` - funkcja toggle
  - `currentUserEmail` - tracking zalogowanego użytkownika
  - localStorage per-user: `fernetKey_${email}`

---

## Roadmap Bezpieczeństwa (Pending)

### 🔜 Segment 3: Rate Limiting + Account Lockouts
- Slowapi lub custom middleware
- Limit failed login attempts
- Temporary account lockout

### 🔜 Segment 4: 2FA TOTP
- pyotp integration
- QR code generation
- TOTP verification for login

### 🔜 Segment 5: Argon2id Key Derivation
- Replace user-generated Fernet keys
- Derive encryption key from master password
- PBKDF2 or Argon2id

### 🔜 Segment 6: Audit Logs + Documentation
- Security event logging
- Login/logout tracking
- Failed authentication attempts
- Operational runbooks

---

## Architektura Aplikacji

### Backend Structure
```
app/
├── main.py              # FastAPI app, CORS, middleware
├── database.py          # SQLAlchemy setup
├── security.py          # JWT, hashing, encryption utils
├── models/
│   ├── user.py         # User ORM model
│   └── password.py     # PasswordEntry ORM model
├── routes/
│   ├── auth.py         # /auth/* endpoints
│   └── password.py     # /passwords/* endpoints
└── schemas/
    ├── user.py         # Pydantic schemas
    └── password.py     # Pydantic schemas
```

### Frontend Structure
```
frontend/frontend-app/
├── src/
│   ├── App.vue         # Main component
│   ├── main.js         # Vue app init
│   └── style.css       # Global styles
├── dist/               # Production build
└── vite.config.js      # Build configuration
```

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL
);

-- Passwords table
CREATE TABLE password_entries (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    service VARCHAR NOT NULL,
    login VARCHAR NOT NULL,
    password VARCHAR NOT NULL,  -- Encrypted with Fernet
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## API Endpoints

### Authentication
- `POST /auth/register` - Rejestracja użytkownika
- `POST /auth/login` - Logowanie (ustawia HttpOnly cookie)
- `POST /auth/logout` - Wylogowanie (usuwa cookie)
- `GET /auth/me` - Pobierz dane zalogowanego użytkownika

### Password Management
- `GET /passwords` - Lista haseł użytkownika
- `POST /passwords` - Dodaj nowe hasło (wymaga klucza Fernet)
- `DELETE /passwords/{id}` - Usuń hasło
- `POST /passwords/decrypt` - Odszyfruj hasło (wymaga klucza Fernet)

---

## Deployment

### Development
```bash
# Backend
python app/main.py

# Frontend build
cd frontend/frontend-app
npm run build
```

### Production Considerations
1. Ustaw `COOKIE_SECURE=true` w .env
2. Użyj HTTPS (nginx/Apache reverse proxy)
3. Zmienna `SECRET_KEY` z bezpiecznego źródła
4. Backup bazy danych regularnie
5. Rate limiting na poziomie reverse proxy

---

## Changelog

### v2.1 - Marzec 2026
- ✅ HttpOnly cookies authentication
- ✅ CORS hardening
- ✅ Security headers + CSP
- ✅ Show/hide password toggle
- ✅ Per-user Fernet key storage

### v2.0 - Poprzednie wersje
- User-generated Fernet keys
- Basic JWT authentication
- CRUD operations for passwords
