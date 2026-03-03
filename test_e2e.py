#!/usr/bin/env python3
"""Test end-to-end: JavaScript generuje klucz -> Python szyfruje -> Python odszyfrowuje"""

from cryptography.fernet import Fernet, InvalidToken
import base64
import os

def simulate_js_key_generation():
    """Symuluje generowanie klucza jak w JavaScript (poprawiona wersja)"""
    array = bytearray(os.urandom(32))
    # JavaScript: btoa(binary)
    base64_key = base64.b64encode(array).decode()
    return base64_key

def encrypt_password(plain_password: str, key: str) -> str:
    """Szyfruje hasło używając klucza (jak w backend)"""
    f = Fernet(key.encode())
    return f.encrypt(plain_password.encode()).decode()

def decrypt_password(encrypted_password: str, key: str) -> str:
    """Odszyfrowuje hasło używając klucza (jak w backend)"""
    f = Fernet(key.encode())
    return f.decrypt(encrypted_password.encode()).decode()

print("=== TEST END-TO-END ===\n")

# 1. Generuj klucz (jak JavaScript)
print("1. Generowanie klucza (JavaScript)...")
key = simulate_js_key_generation()
print(f"   Klucz: {key}")
print(f"   Długość: {len(key)} znaków\n")

# 2. Zaszyfruj hasło (jak w endpoint /passwords POST)
test_password = "moje_super_haslo_123"
print(f"2. Szyfrowanie hasła: '{test_password}'")
try:
    encrypted = encrypt_password(test_password, key)
    print(f"   Zaszyfrowane: {encrypted}\n")
except Exception as e:
    print(f"   ❌ BŁĄD podczas szyfrowania: {e}\n")
    exit(1)

# 3. Odszyfruj hasło (jak w endpoint /passwords/decrypt POST)
print(f"3. Odszyfrowanie hasła tym samym kluczem...")
try:
    decrypted = decrypt_password(encrypted, key)
    print(f"   Odszyfrowane: {decrypted}\n")
    
    if decrypted == test_password:
        print("✅ SUKCES! Hasło zostało poprawnie zaszyfrowane i odszyfrowane!")
    else:
        print(f"❌ BŁĄD! Odszyfrowane hasło nie pasuje!")
        print(f"   Oczekiwano: {test_password}")
        print(f"   Otrzymano:  {decrypted}")
except InvalidToken:
    print(f"   ❌ BŁĄD: Nieprawidłowy token/klucz!\n")
except Exception as e:
    print(f"   ❌ BŁĄD podczas odszyfrowania: {e}\n")
    exit(1)

# 4. Test z różnymi kluczami (powinien się nie udać)
print("\n4. Test z innym kluczem (powinien się nie udać)...")
wrong_key = simulate_js_key_generation()
try:
    decrypt_password(encrypted, wrong_key)
    print("   ❌ PROBLEM! Udało się odszyfrować z innym kluczem!")
except InvalidToken:
    print("   ✅ Dobrze! Inny klucz nie może odszyfrować hasła.")
except Exception as e:
    print(f"   ✅ Dobrze! Błąd: {e}")
