Aplikacja menadżera haseł umożliwiająca bezpieczne generowanie, przechowywanie i zarządzanie hasłami użytkownika.

## 🛠️ Technologie

- **Frontend:** Vue 3, Vite
- **Backend:** FastAPI (Python)
- **Baza danych:** SQLite
- **Inne:** SQLAlchemy, Pydantic, JWT

## 🚀 Uruchomienie aplikacji

### Szybki start (lokalnie)

1. Zainstaluj backend:
   - Wejdź do folderu `app/` i zainstaluj zależności z `requirements.txt`.
2. Zbuduj frontend:
   - Wejdź do folderu `frontend/frontend-app/`, zainstaluj zależności i wykonaj build.
3. Uruchom backend:
   - Uruchom `app/main.py`. Backend serwuje zbudowany frontend z `frontend/frontend-app/dist`.
4. Otwórz w przeglądarce:
   - `http://localhost:8000`

### Uruchomienie na Replit

1. Zainstaluj zależności backendu z `app/requirements.txt`.
2. Zbuduj frontend w `frontend/frontend-app/` (powstaje `dist/`).
3. W ustawieniach Replit uruchamiaj komendę:
   - `python app/main.py`
4. Otwórz publiczny URL replita.