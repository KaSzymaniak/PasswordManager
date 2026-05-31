Aplikacja: prosty menedżer haseł (backend API + frontend Vue).

**Technologie**
- Frontend: Vue 3 + Vite
- Backend: FastAPI (Python)
- DB: SQLite (domyślnie `passwords.db`)
- Szyfrowanie: Fernet (cryptography)
- Autentykacja: JWT, bcrypt

Krótka instrukcja uruchomienia lokalnie

1) Utwórz i aktywuj virtualenv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Zainstaluj zależności backend:

```powershell
pip install -r requirements.txt
```

3) (Opcjonalnie) utwórz plik `.env` w katalogu projektu z ustawieniami, np:

```
SECRET_KEY=zmien_to_na_coś_trudnego
DATABASE_URL=sqlite:///./passwords.db
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:8000
COOKIE_SECURE=false
```

4) Uruchom backend (z katalogu projektu):

```powershell
uvicorn app.main:app --reload --port 8000
```

5) Frontend (dev):

```powershell
cd frontend/frontend-app
npm install
npm run dev
```

Frontend dev działa zwykle na `http://localhost:5173`. Po zbudowaniu (`npm run build`) backend spróbuje serwować pliki z `frontend/frontend-app/dist`.

Gdzie sprawdzić API

- Interfejs Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

Uwagi / typowe problemy

- Błąd "No module named 'database'": uruchamiaj aplikację jako pakiet (`uvicorn app.main:app`), nie `main.py` z innego katalogu — poprawne importy używają prefiksu `app.` (już zaktualizowane).
- Domyślnie używany jest SQLite — plik `passwords.db` zostanie utworzony w katalogu projektu.

Chcesz, żebym dodał jeszcze sekcję z opisem endpointów API lub przykładowe curl/HTTPie przykłady?*** End Patch