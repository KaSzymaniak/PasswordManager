# Instrukcja Migracji - v1.0 → v2.0

## ⚠️ Ważne - Breaking Changes

Wersja 2.0 wprowadza **niezgodność wsteczną** z poprzednim systemem szyfrowania.

### Co się zmieniło?

**Wersja 1.0:**
- Jeden globalny klucz Fernet w pliku `.env`
- Wszystkie hasła szyfrowane tym samym kluczem
- Administrator serwera ma dostęp do klucza

**Wersja 2.0:**
- **Każdy użytkownik ma swój własny klucz**
- Klucze generowane w przeglądarce (bezpieczne)
- Administrator **NIE MA dostępu** do kluczy użytkowników
- System "zero-knowledge"

## 🔄 Migracja

### Jeśli masz stare hasła w bazie danych:

**OPCJA 1: Start od zera (zalecane)**
```bash
# Usuń starą bazę danych
rm passwords.db  # Linux/Mac
Remove-Item passwords.db -Force  # Windows PowerShell

# Uruchom aplikację - nowa baza zostanie utworzona automatycznie
python app/main.py
```

**OPCJA 2: Eksport i Re-import**
1. **Przed aktualizacją**: Wyeksportuj hasła z GUI (jeśli była taka funkcja)
2. Zaktualizuj kod
3. Usuń starą bazę: `rm passwords.db`
4. Wygeneruj nowy klucz w aplikacji
5. Ręcznie dodaj hasła ponownie

### Jeśli zaczynasz od zera:

Po prostu uruchom aplikację - wszystko zadziała automatycznie! 🎉

## 📋 Checklist Aktualizacji

- [ ] Zrób backup bazy danych (jeśli masz ważne dane)
- [ ] Wyeksportuj hasła (jeśli potrzebujesz ich zachować)
- [ ] Zaktualizuj kod (`git pull`)
- [ ] Usuń plik `app/.env` (lub usuń linię `FERNET_KEY=...`)
- [ ] Usuń starą bazę danych `passwords.db`
- [ ] Przebuduj frontend: `cd frontend/frontend-app && npm run build`
- [ ] Uruchom aplikację: `python app/main.py`
- [ ] Wygeneruj nowy klucz Fernet w aplikacji
- [ ] **ZAPISZ KLUCZ w bezpiecznym miejscu!**

## 🆘 Pomoc

### Problem: "Nieprawidłowy klucz"
- Sprawdź czy używasz **tego samego klucza** którego użyłeś do szyfrowania
- Klucz musi mieć dokładnie 44 znaki
- Klucz jest case-sensitive (wielkie/małe litery mają znaczenie)

### Problem: "Nie widzę odszyfrowanego hasła"
- Upewnij się, że wpisałeś klucz w żółtej sekcji
- Kliknij przycisk "Pokaż"
- Sprawdź konsolę przeglądarki (F12) w celu zobaczyć logi

### Problem: "Zgubiłem klucz"
- Jeśli klucz był zapisany w localStorage przeglądarki - sprawdź:
  - `F12` → `Application` → `Local Storage` → `http://localhost:8000` → `fernetKey`
- Jeśli nie - niestety hasła są bezpowrotnie stracone (to nie bug, to feature bezpieczeństwa!)

## 📞 Kontakt

W przypadku problemów otwórz Issue na GitHubie:
https://github.com/KaSzymaniak/PasswordManager/issues

---

**Data ostatniej aktualizacji**: 2026-03-02  
**Wersja dokumentu**: 1.0
