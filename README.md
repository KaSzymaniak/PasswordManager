# Menedżer Haseł

Aplikacja webowa do bezpiecznego przechowywania haseł z szyfrowaniem
wykonywanym w całości w przeglądarce (model zero-knowledge).

## Bezpieczeństwo

- **Szyfrowanie end-to-end**: PIN + klucz sejfu + sól konta są łączone w przeglądarce (PBKDF2 → AES-256-GCM) w klucz szyfrujący
- **Zero-knowledge**: serwer nie ma dostępu do PIN-u, klucza sejfu ani haseł w postaci jawnej - przechowuje wyłącznie szyfrogramy
- **Brak trwałego zapisu**: PIN i klucz sejfu istnieją tylko w pamięci sesji przeglądarki - wpisuje się je po każdym zalogowaniu
- **Konto odzyskiwalne, sejf nie**: hasło logowania można zresetować kodem wysłanym mailem, PIN-u ani klucza sejfu nie da się odzyskać (szczegóły: `docs/RECOVERY.md`)

## Technologie

- **Frontend:** Vue 3, Vite
- **Backend:** FastAPI (Python)
- **Baza danych:** SQLite (SQLAlchemy)
- **Kryptografia:** Web Crypto API - PBKDF2-HMAC-SHA256, AES-256-GCM
- **Autentykacja:** JWT w ciasteczku HttpOnly, hashowanie haseł bcrypt
- **Walidacja:** Pydantic

## Uruchomienie

1. Zainstaluj zależności backendu (z katalogu głównego repozytorium):
   ```bash
   pip install -r requirements.txt
   ```
2. Zbuduj frontend:
   ```bash
   cd frontend/frontend-app
   npm install
   npm run build
   ```
3. Uruchom backend (z katalogu głównego repozytorium):
   ```bash
   python -m uvicorn app.main:app --reload --reload-dir app
   ```
   Backend serwuje zbudowany frontend z `frontend/frontend-app/dist`.
4. Otwórz w przeglądarce `http://localhost:8000`.

### Konfiguracja (opcjonalna)

Aplikacja działa bez dodatkowej konfiguracji. Opcjonalne zmienne można
umieścić w pliku `.env` w katalogu głównym:

| Zmienna | Znaczenie | Domyślnie |
|---|---|---|
| `SECRET_KEY` | Klucz podpisujący tokeny JWT | losowy przy każdym starcie (sesje wygasają po restarcie serwera) |
| `COOKIE_SECURE` | Ciasteczko tylko przez HTTPS | `false` |
| `CORS_ALLOWED_ORIGINS` | Dozwolone originy (po przecinku) | `http://localhost:8000,http://127.0.0.1:8000` |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM` | Wysyłka kodów weryfikacyjnych mailem | brak - kody są wypisywane w konsoli serwera |

Stały `SECRET_KEY` można wygenerować poleceniem:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Jak używać

### Rejestracja i logowanie

1. **Zarejestruj się** podając email i hasło (min. 8 znaków, mała i wielka litera, cyfra, znak specjalny)
2. **Potwierdź email** kodem - bez skonfigurowanego SMTP kod pojawia się w konsoli serwera
3. **Zaloguj się**

### Pierwsze odblokowanie sejfu

1. Wpisz **PIN** (min. 4 cyfry)
2. Kliknij **„Generuj nowy klucz”** - wyświetli się nowy klucz sejfu
3. **Zapisz klucz** w bezpiecznym miejscu (np. na kartce) i potwierdź to w oknie
4. Kliknij **„Odblokuj sejf”**

Przy kolejnych logowaniach wpisujesz ten sam PIN i klucz sejfu, a następnie
klikasz „Odblokuj sejf”. Błędna kombinacja jest odrzucana.

### Zarządzanie hasłami

- **Dodawanie**: wypełnij pola Serwis, Login, Hasło i kliknij „Dodaj” - hasło jest szyfrowane w przeglądarce przed wysłaniem
- **Podgląd**: „Pokaż” odszyfrowuje hasło lokalnie, „Ukryj” chowa je ponownie
- **Usuwanie**: „Usuń” i potwierdzenie

## Ważne informacje o bezpieczeństwie

- **Dwa niezależne sekrety**: PIN (zapamiętany) i klucz sejfu (zapisany poza aplikacją) - oba są potrzebne do odszyfrowania sejfu
- **Utrata**: zgubienie PIN-u lub klucza oznacza bezpowrotną utratę zapisanych haseł - to celowy kompromis modelu zero-knowledge (`docs/RECOVERY.md`)
- **Administrator serwera** nie może odszyfrować haseł użytkowników - w bazie znajdują się wyłącznie szyfrogramy AES-GCM

## Struktura projektu

```
PasswordManager/
├── app/                        # Backend (FastAPI)
│   ├── main.py                 # Punkt wejścia, CORS, nagłówki bezpieczeństwa
│   ├── database.py             # Konfiguracja SQLAlchemy, migracja kolumn
│   ├── security.py             # JWT, hashowanie haseł (bcrypt)
│   ├── email_utils.py          # Wysyłka kodów (SMTP lub log serwera)
│   ├── models/                 # Modele ORM (User, PasswordEntry)
│   ├── routes/                 # Endpointy /auth, /passwords, /vault
│   └── schemas/                # Modele Pydantic
├── frontend/
│   └── frontend-app/           # Frontend (Vue 3 + Vite)
│       └── src/
│           ├── App.vue         # Interfejs aplikacji
│           └── crypto.js       # PBKDF2 + AES-GCM (Web Crypto API)
├── docs/
│   ├── architecture.md         # Architektura i model bezpieczeństwa
│   ├── RECOVERY.md             # Model odzyskiwania i zagrożeń
│   ├── CHANGELOG.md            # Historia zmian
│   └── MIGRATION.md            # Instrukcje migracji między wersjami
├── test_api.py                 # Test pełnego przepływu API
├── test_detailed.py            # Test API ze szczegółowym wydrukiem odpowiedzi
├── check_db.py                 # Podgląd zawartości bazy SQLite
└── requirements.txt            # Zależności backendu
```

## Testy

Przy uruchomionym backendzie (z katalogu głównego):
```bash
python test_api.py
python test_detailed.py
```
