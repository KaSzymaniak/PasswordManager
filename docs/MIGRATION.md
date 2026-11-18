# Instrukcje migracji

## v2.x → v3.x

### Zakres zmian

Wersja 3.0 przenosi **całe szyfrowanie haseł do przeglądarki** i usuwa
szyfrowanie Fernet po stronie serwera.

**Wersja 2.x:**
- Serwer szyfrował i odszyfrowywał hasła algorytmem Fernet, otrzymując klucz
  użytkownika w każdym żądaniu
- Endpoint `POST /passwords/decrypt` odszyfrowywał hasło na backendzie

**Wersja 3.x:**
- Szyfrowanie i odszyfrowanie odbywa się wyłącznie w przeglądarce (Web Crypto API)
- Klucz AES-256-GCM jest wyprowadzany z PIN-u, klucza sejfu i soli konta
  przez PBKDF2 (310 000 iteracji, SHA-256) i nie opuszcza przeglądarki
- Serwer przechowuje wyłącznie szyfrogram w base64
- Endpoint `POST /passwords/decrypt` został usunięty
- (3.1) Weryfikator sejfu - błędna kombinacja PIN + klucz sejfu jest
  odrzucana przy odblokowaniu
- (3.1) Klucz generowany przez użytkownika nosi nazwę „klucz sejfu”
  (wcześniej „klucz Fernet”) - zmiana dotyczy wyłącznie nazwy, istniejące
  klucze działają bez zmian

### Migracja danych

Hasła zaszyfrowane po stronie serwera (Fernet) nie są kompatybilne z nowym
formatem - różni się zarówno format szyfrogramu, jak i sposób wyznaczania
klucza. Na etapie rozwoju projektu jedyną wspieraną ścieżką jest utworzenie
bazy od nowa:

```bash
# Linux / macOS
rm passwords.db
# Windows PowerShell
Remove-Item passwords.db -Force

# Nowa baza zostanie utworzona automatycznie przy starcie
python -m uvicorn app.main:app --reload --reload-dir app
```

Przy aktualizacji z 3.0 do 3.1 reset bazy nie jest wymagany - brakująca
kolumna `vault_verifier` jest dodawana automatycznie, a weryfikator zostaje
utworzony przy pierwszym poprawnym odblokowaniu sejfu.

### Lista kroków

1. Zaktualizuj kod (`git pull`)
2. Usuń bazę `passwords.db` (tylko przy przejściu z 2.x)
3. Zainstaluj zależności: `pip install -r requirements.txt`
4. Zbuduj frontend: `cd frontend/frontend-app && npm install && npm run build`
5. Uruchom aplikację: `python -m uvicorn app.main:app --reload --reload-dir app`
6. Ustaw PIN, wygeneruj nowy klucz sejfu i zapisz go w bezpiecznym miejscu

### Najczęstsze problemy

**„Zły PIN lub klucz sejfu”** - należy podać dokładnie tę samą kombinację
PIN + klucz sejfu, która została użyta przy pierwszym odblokowaniu sejfu.
Komunikat celowo nie rozróżnia, który ze składników jest błędny.

**Utrata PIN-u lub klucza** - oba istnieją wyłącznie w pamięci sesji
przeglądarki i nie są przechowywane na serwerze, dlatego zapisanych haseł
nie da się odzyskać. Wynika to bezpośrednio z modelu zero-knowledge
(`docs/RECOVERY.md`).

---

## v1.x → v2.x

### Zakres zmian

**Wersja 1.x:**
- Jeden globalny klucz Fernet w pliku `.env`
- Wszystkie hasła szyfrowane tym samym kluczem, dostępnym dla administratora serwera

**Wersja 2.x:**
- Każdy użytkownik generuje własny klucz Fernet w przeglądarce
- Klucz nie jest przechowywany na serwerze

### Migracja danych

Hasła zaszyfrowane kluczem globalnym nie są kompatybilne z kluczami
użytkowników. Należy usunąć bazę `passwords.db` oraz zmienną `FERNET_KEY`
z pliku `.env`, a następnie wygenerować nowy klucz w aplikacji i ponownie
dodać hasła.
