#!/usr/bin/env python3
"""Test Fernet key generation and encryption/decryption"""

from cryptography.fernet import Fernet
import base64

print("=== Test 1: Python generuje klucz ===")
python_key = Fernet.generate_key()
print(f"Klucz wygenerowany przez Python: {python_key.decode()}")
print(f"Długość: {len(python_key.decode())} znaków")

f = Fernet(python_key)
test_password = "testowe_haslo_123"
encrypted = f.encrypt(test_password.encode())
print(f"Zaszyfrowane: {encrypted.decode()}")

decrypted = f.decrypt(encrypted)
print(f"Odszyfrowane: {decrypted.decode()}")
print(f"✅ Python -> Python działa!\n")

print("=== Test 2: Symulacja JavaScript generowania klucza ===")
# JavaScript robi: crypto.getRandomValues(32 bajty) -> btoa()
import os
random_bytes = os.urandom(32)
print(f"32 losowe bajty (hex): {random_bytes.hex()}")

# JavaScript btoa() = standardowy base64 (nie URL-safe!)
js_key = base64.b64encode(random_bytes).decode()
print(f"Klucz jak w JavaScript (base64): {js_key}")
print(f"Długość: {len(js_key)} znaków")

# Próba użycia tego klucza w Fernet
try:
    f2 = Fernet(js_key.encode())
    encrypted2 = f2.encrypt(test_password.encode())
    print(f"Zaszyfrowane: {encrypted2.decode()}")
    decrypted2 = f2.decrypt(encrypted2)
    print(f"Odszyfrowane: {decrypted2.decode()}")
    print(f"✅ JavaScript klucz działa!\n")
except Exception as e:
    print(f"❌ BŁĄD: {e}\n")

print("=== Test 3: URL-safe base64 (właściwy dla Fernet) ===")
# Fernet wymaga URL-safe base64
urlsafe_key = base64.urlsafe_b64encode(random_bytes).decode()
print(f"Klucz URL-safe base64: {urlsafe_key}")
print(f"Długość: {len(urlsafe_key)} znaków")

try:
    f3 = Fernet(urlsafe_key.encode())
    encrypted3 = f3.encrypt(test_password.encode())
    print(f"Zaszyfrowane: {encrypted3.decode()}")
    decrypted3 = f3.decrypt(encrypted3)
    print(f"Odszyfrowane: {decrypted3.decode()}")
    print(f"✅ URL-safe base64 działa!\n")
except Exception as e:
    print(f"❌ BŁĄD: {e}\n")

print("\n=== WNIOSKI ===")
print(f"Python Fernet.generate_key(): {python_key.decode()}")
print(f"JavaScript btoa():             {js_key}")
print(f"URL-safe base64:               {urlsafe_key}")
print("\nRóżnica między btoa() a URL-safe:")
print("  btoa() używa: +, /")
print("  URL-safe używa: -, _")
