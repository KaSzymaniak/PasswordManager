// Szyfrowanie sejfu po stronie przeglądarki: PBKDF2 (wyprowadzenie klucza)
// + AES-GCM (szyfrowanie/odszyfrowanie). Serwer przechowuje wyłącznie
// szyfrogram w base64 i nie uczestniczy w żadnej operacji kryptograficznej.

const PBKDF2_ITERATIONS = 310000; // minimum zalecane przez OWASP dla PBKDF2-SHA256
const IV_LENGTH_BYTES = 12; // standardowa długość wektora IV dla AES-GCM
const VERIFIER_PLAINTEXT = "vault-ok";

function bytesToBase64(bytes) {
  let binary = "";
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}

function base64ToBytes(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

/**
 * Wyprowadza klucz AES-256-GCM z PIN-u, klucza sejfu i soli konta
 * (GET /vault/salt). Klucz nie jest nigdzie zapamiętywany - liczony jest
 * od nowa przy każdej operacji szyfrowania/odszyfrowania.
 */
export async function deriveEncryptionKey(pin, vaultKey, saltBase64) {
  const passphrase = `${pin}:${vaultKey}`;
  const passphraseBytes = new TextEncoder().encode(passphrase);
  const saltBytes = base64ToBytes(saltBase64);

  const keyMaterial = await crypto.subtle.importKey(
    "raw",
    passphraseBytes,
    "PBKDF2",
    false,
    ["deriveKey"]
  );

  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: saltBytes,
      iterations: PBKDF2_ITERATIONS,
      hash: "SHA-256",
    },
    keyMaterial,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"]
  );
}

/**
 * Szyfruje tekst kluczem szyfrującym (AES-GCM) z losowym IV.
 * Zwraca base64(IV || szyfrogram+tag) - pojedynczy ciąg zapisywany
 * bez zmian w PasswordEntry.password.
 */
export async function encryptText(plainText, encryptionKey) {
  const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH_BYTES));
  const plainBytes = new TextEncoder().encode(plainText);
  const ciphertext = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, encryptionKey, plainBytes);

  const combined = new Uint8Array(iv.length + ciphertext.byteLength);
  combined.set(iv, 0);
  combined.set(new Uint8Array(ciphertext), iv.length);
  return bytesToBase64(combined);
}

/**
 * Odszyfrowuje base64(IV || szyfrogram+tag) kluczem szyfrującym.
 * Przy złym PIN-ie lub kluczu weryfikacja tagu AES-GCM się nie powiedzie
 * i funkcja rzuci wyjątek (OperationError) - bez rozróżnienia, który
 * składnik jest błędny.
 */
export async function decryptText(blobBase64, encryptionKey) {
  const combined = base64ToBytes(blobBase64);
  const iv = combined.slice(0, IV_LENGTH_BYTES);
  const ciphertext = combined.slice(IV_LENGTH_BYTES);
  const plainBuf = await crypto.subtle.decrypt({ name: "AES-GCM", iv }, encryptionKey, ciphertext);
  return new TextDecoder().decode(plainBuf);
}

/**
 * Weryfikator sejfu: znana stała zaszyfrowana kluczem szyfrującym, przechowywana
 * na serwerze obok soli. Pozwala sprawdzić poprawność PIN-u i klucza sejfu
 * łącznie (nigdy samego PIN-u) przed zapisaniem czegokolwiek.
 */
export function createVerifier(encryptionKey) {
  return encryptText(VERIFIER_PLAINTEXT, encryptionKey);
}

export async function checkVerifier(blobBase64, encryptionKey) {
  try {
    return (await decryptText(blobBase64, encryptionKey)) === VERIFIER_PLAINTEXT;
  } catch {
    return false;
  }
}
