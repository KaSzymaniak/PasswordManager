# Changelog - Historia Zmian

## [2.0.0] - 2026-03-02

### 🔐 Główne Zmiany - System Szyfrowania

#### Zmieniono
- **System szyfrowania haseł**: Przejście z globalnego klucza Fernet do kluczy generowanych przez użytkowników
- **Bezpieczeństwo**: Każdy użytkownik teraz generuje i przechowuje swój własny klucz Fernet
- **Backend**: Usunięto wymaganie FERNET_KEY z pliku `.env`

#### Dodano
- **Generator kluczy Fernet w przeglądarce**: Przycisk "🔑 Generuj nowy klucz"
- **localStorage**: Automatyczne zapisywanie klucza w przeglądarce
- **Szczegółowe logowanie**: Backend i frontend teraz logują operacje szyfrowania/odszyfrowania
- **Walidacja kluczy**: Sprawdzanie formatu klucza przed operacjami

#### Naprawiono
- **Generowanie klucza w JavaScript**: Poprawiono konwersję bajtów do base64
- **Vue 3 kompatybilność**: Zamieniono `this.$set()` na zwykłe przypisanie
- **Szyfrowanie**: Klucz Fernet jest teraz przekazywany przy każdej operacji

### 📁 Zmiany w Plikach

#### Backend (`app/`)
- **security.py**:
  - Usunięto globalny klucz Fernet z `.env`
  - `encrypt_text()` teraz przyjmuje klucz jako parametr
  - `decrypt_text()` teraz przyjmuje klucz jako parametr

- **routes/password.py**:
  - Endpoint `POST /passwords`: wymaga klucza w payload
  - Endpoint `POST /passwords/decrypt`: używa klucza z payload
  - Endpoint `PUT /passwords/{id}`: wymaga klucza do reszyfrowania
  - Dodano szczegółowe logowanie wszystkich operacji

- **schemas/password.py**:
  - Dodano pole `key: str` do `PasswordCreate`

- **.env**:
  - Usunięto `FERNET_KEY` (nie jest już potrzebny)

#### Frontend (`frontend/frontend-app/src/`)
- **App.vue**:
  - Dodano funkcję `generateFernetKey()` - generuje klucz w przeglądarce
  - Dodano pole input dla klucza Fernet (z żółtym tłem)
  - `addPassword()`: wysyła klucz wraz z hasłem
  - `decryptPassword()`: używa klucza do odszyfrowania
  - Klucz jest zapisywany w `localStorage`
  - Naprawiono `this.$set()` → `this.decrypted[id] = ...` (Vue 3)
  - Dodano szczegółowe `console.log()` dla debugowania

### 🔬 Pliki Testowe (dodane)
- `test_fernet.py` - Test generowania kluczy Fernet
- `test_e2e.py` - Test end-to-end szyfrowania
- `test_api.py` - Test API przez HTTP
- `test_detailed.py` - Szczegółowy test flow użytkownika
- `check_db.py` - Narzędzie do inspekcji bazy danych

### ⚠️ Breaking Changes
- **Stare hasła są niekompatybilne**: Hasła zaszyfrowane starym systemem NIE MOGĄ być odszyfrowane nowym systemem
- **Wymagany reset bazy**: Należy usunąć starą bazę danych `passwords.db`
- **Użytkownicy muszą wygenerować nowy klucz**: Stary klucz z `.env` nie działa

### 🚀 Jak Używać (Nowa Wersja)

1. Otwórz aplikację w przeglądarce
2. Zaloguj się lub zarejestruj
3. Kliknij "🔑 Generuj nowy klucz" w żółtej sekcji
4. **ZAPISZ KLUCZ W BEZPIECZNYM MIEJSCU** (np. w menedżerze haseł)
5. Dodawaj hasła - będą szyfrowane Twoim kluczem
6. Kliknij "Pokaż" aby odszyfrować hasło

### 🔒 Bezpieczeństwo

**Zalety nowego systemu:**
- ✅ Każdy użytkownik ma swój własny klucz szyfrujący
- ✅ Klucz NIE jest przechowywany na serwerze
- ✅ Bez klucza hasła są bezpowrotnie zaszyfrowane
- ✅ Administrator serwera NIE MOŻE odszyfrować haseł użytkowników

**Ważne ostrzeżenia:**
- ⚠️ **Utrata klucza = utrata dostępu do haseł**
- ⚠️ Klucz jest przechowywany w `localStorage` przeglądarki
- ⚠️ Po wyczyszczeniu danych przeglądarki klucz zostanie usunięty
- ⚠️ **KONIECZNIE zapisz klucz poza przeglądarką**

### 📊 Statystyki

- Pliki zmienione: 5
- Dodane linie: ~150
- Usunięte linie: ~50
- Nowe funkcje: 1 (generator kluczy)
- Naprawione błędy: 2 (konwersja base64, Vue 3 reaktywność)
