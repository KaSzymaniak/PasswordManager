# Model Odzyskiwania i Zagrożeń

Ten dokument opisuje wprost: co w tej aplikacji da się odzyskać po
zgubieniu, co nie da się odzyskać **z premedytacją**, i dlaczego. To nie
jest brak funkcji - to świadomy kompromis bezpieczeństwa typowy dla
menedżerów haseł zero-knowledge.

## Dwie niezależne warstwy

Aplikacja rozdziela dwie rzeczy, które łatwo pomylić:

1. **Konto** - kto się loguje do aplikacji (email + hasło).
2. **Sejf** - co odszyfrowuje zapisane hasła (PIN + klucz sejfu).

Te warstwy są **celowo niezależne**. Gdyby klucz szyfrujący wynikał z hasła
logowania, reset hasła przez email dawałby dostęp do sejfu każdemu, kto
przejmie skrzynkę pocztową. Niezależny PIN pozwala też w przyszłości dodać
logowanie zewnętrzne (np. Google OAuth), w którym aplikacja w ogóle nie zna
hasła użytkownika.

## Co jest odzyskiwalne: Konto

Jeśli zapomnisz hasła logowania:

1. `POST /auth/forgot-password` - podajesz email, dostajesz kod.
2. `POST /auth/reset-password` - kod + nowe hasło.

To odzyskuje dostęp do **aplikacji**, nie do **haseł w sejfie** - logowanie
z nowym hasłem samo w sobie nic nie odszyfrowuje.

## Co NIE jest odzyskiwalne: Sejf (PIN + klucz sejfu)

Jeśli zgubisz PIN lub klucz sejfu (albo oba) - **zapisane hasła są
bezpowrotnie stracone.** Serwer nigdy ich nie widział w postaci jawnej,
więc nie ma czego przywrócić.

Powód: PIN + klucz sejfu + sól konta (`kdf_salt`, `GET /vault/salt`)
łączą się przez PBKDF2 (310 000 iteracji, SHA-256) w klucz AES-256-GCM,
**wyłącznie w przeglądarce**. Serwer przechowuje tylko wynikowy szyfrogram
(`base64(IV || ciphertext+tag)`) - nieprzejrzysty ciąg, z którego nie da
się odtworzyć ani PIN-u, ani klucza, ani hasła.

To jest **zero-knowledge**: nawet pełny dostęp do bazy danych i kodu
serwera nie wystarczy, żeby odszyfrować czyjekolwiek hasła bez PIN-u i
klucza sejfu tej osoby.

### Co robić, żeby nie stracić dostępu

- Zapisz klucz sejfu **fizycznie** (kartka, sejf, inny menedżer haseł) -
  wygenerowany raz, modal wymaga potwierdzenia że go zapisałeś.
- Zapamiętaj PIN - jak każde hasło, którego używasz regularnie.
