Aplikacja menadżera haseł umożliwiająca bezpieczne generowanie, przechowywanie i zarządzanie hasłami użytkownika.

## � Bezpieczeństwo

- **Szyfrowanie end-to-end**: Każdy użytkownik generuje swój własny klucz Fernet
- **Zero-knowledge**: Serwer NIE ma dostępu do kluczy szyfrujących użytkowników
- **Lokalne przechowywanie klucza**: Klucz jest zapisywany w localStorage przeglądarki
- ⚠️ **Ważne**: Zapisz klucz Fernet w bezpiecznym miejscu - bez niego nie odzyskasz haseł!

## 🛠️ Technologie

- **Frontend:** Vue 3, Vite
- **Backend:** FastAPI (Python)
- **Baza danych:** SQLite
- **Szyfrowanie:** Fernet (cryptography)
- **Autentykacja:** JWT, bcrypt
- **Inne:** SQLAlchemy, Pydantic

## 🚀 Uruchomienie aplikacji

### Szybki start (lokalnie)

1. Zainstaluj backend:
   - Wejdź do folderu `app/` i zainstaluj zależności z `requirements.txt`.
   - Komendy: `cd app` → `py -m pip install -r requirements.txt`
2. Zbuduj frontend:
   - Wejdź do folderu `frontend/frontend-app/`, zainstaluj zależności i wykonaj build.
   - Komendy: `cd frontend/frontend-app` → `npm install` → `npm run build`
3. Uruchom backend:
   - Uruchom `app/main.py`. Backend serwuje zbudowany frontend z `frontend/frontend-app/dist`.
   - Komenda: `python app/main.py`
4. Otwórz w przeglądarce:
   - `http://localhost:8000`

### Uruchomienie na Replit

1. Zainstaluj zależności backendu z `app/requirements.txt`.
   - Komendy: `cd app` → `pip install -r requirements.txt`
2. Zbuduj frontend w `frontend/frontend-app/` (powstaje `dist/`).
   - Komendy: `cd frontend/frontend-app` → `npm install` → `npm run build`
3. W ustawieniach Replit uruchamiaj komendę:
   - `python app/main.py`
4. Otwórz publiczny URL replita.

## 📖 Jak używać

### Pierwsze uruchomienie

1. **Zarejestruj się** - utwórz konto podając email i hasło
2. **Zaloguj się** - wprowadź swoje dane logowania
3. **Wygeneruj klucz Fernet** - kliknij przycisk "🔑 Generuj nowy klucz"
4. **ZAPISZ KLUCZ!** - skopiuj i zapisz klucz w bezpiecznym miejscu (np. w innym menedżerze haseł)
   - ⚠️ Bez tego klucza NIE ODSZYFRUJESZ swoich haseł!
   - Klucz wygląda np. tak: `wRs7fzBk1FQMskeg+wBu8GEo88onobj+xB4jnNBEw67Ss=`

### Dodawanie haseł

1. Upewnij się, że **klucz Fernet jest wpisany** w żółtej sekcji
2. Wypełnij formularz:
   - **Serwis**: Nazwa serwisu (np. "Facebook", "Gmail")
   - **Login**: Nazwa użytkownika lub email
   - **Hasło**: Hasło do tego serwisu
3. Kliknij **"Dodaj"**
4. Hasło zostanie **zaszyfrowane** Twoim kluczem i zapisane w bazie

### Wyświetlanie haseł

1. Upewnij się, że **klucz Fernet jest wpisany** (ten sam, którego użyłeś do szyfrowania)
2. Kliknij **"Pokaż"** przy wybranym haśle
3. Hasło zostanie odszyfrowane i wyświetlone zamiast `***`

### Usuwanie haseł

1. Kliknij **"Usuń"** przy wybranym haśle
2. Potwierdź usunięcie

## ⚠️ Ważne Informacje o Bezpieczeństwie

### Klucz Fernet

- **Jeden użytkownik = jeden klucz**: Użyj tego samego klucza dla wszystkich swoich haseł
- **Przechowywanie**: Klucz jest automatycznie zapisywany w `localStorage` przeglądarki
- **Backup**: **KONIECZNIE** zapisz klucz poza przeglądarką (w pliku, notatniku, innym menedżerze haseł)
- **Utrata klucza**: Jeśli zgubisz klucz, **hasła są bezpowrotnie stracone**
- **Zmiana przeglądarki**: Jeśli zmienisz przeglądarkę/komputer, musisz wprowadzić klucz ponownie

### Co się dzieje z Twoimi danymi?

- **Hasła**: Przechowywane **zaszyfrowane** w bazie SQLite na serwerze
- **Klucz szyfrujący**: **NIE** jest przechowywany na serwerze, tylko w Twojej przeglądarce
- **Administrator serwera**: **NIE MOŻE** odszyfrować Twoich haseł bez klucza
- **Bezpieczeństwo**: System typu "zero-knowledge" - tylko Ty znasz swój klucz

## 📁 Struktura Projektu