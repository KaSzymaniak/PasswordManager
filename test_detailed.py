#!/usr/bin/env python3
"""
Szczegółowy test - dokładnie jak użytkownik w przeglądarce
"""

import requests
import base64
import os
from cryptography.fernet import Fernet
import time

API_URL = "http://localhost:8000"

print("="*70)
print("TEST: Generuj klucz -> Dodaj hasło -> Odszyfruj hasło")
print("="*70)

# Czekaj na serwer
time.sleep(1)

# 1. Generuj klucz (DOKŁADNIE jak w JavaScript)
print("\n[1] Generowanie klucza Fernet (jak JavaScript)...")
array = bytearray(os.urandom(32))
# Symuluj JavaScript
binary = ''.join(chr(b) for b in array)
fernet_key = base64.b64encode(binary.encode('latin1')).decode()

print(f"    Klucz: {fernet_key}")
print(f"    Długość: {len(fernet_key)} znaków")

# Sprawdź czy klucz jest OK
try:
    f_test = Fernet(fernet_key.encode())
    print(f"    ✅ Klucz poprawny dla Fernet")
except Exception as e:
    print(f"    ❌ Klucz niepoprawny: {e}")
    exit(1)

# 2. Rejestracja  
print("\n[2] Rejestracja użytkownika...")
email = f"user_{os.urandom(4).hex()}@test.com"
password = "Test123!"
r = requests.post(f"{API_URL}/auth/register", json={"email": email, "password": password})
print(f"    Status: {r.status_code}")

# 3. Logowanie
print("\n[3] Logowanie...")
r = requests.post(f"{API_URL}/auth/login", json={"email": email, "password": password})
token = r.json()["access_token"]
print(f"    ✅ Token: {token[:30]}...")

# 4. Dodaj hasło
print("\n[4] Dodawanie hasła...")
print(f"    Używany klucz: {fernet_key}")
test_password = "MojeHaslo123!"
r = requests.post(f"{API_URL}/passwords", 
    json={
        "service": "Test Service",
        "login": "testuser",
        "password": test_password,
        "key": fernet_key
    },
    headers={"Authorization": f"Bearer {token}"}
)
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    encrypted = data["password"]
    print(f"    ✅ Dodano hasło")
    print(f"    Zaszyfrowane: {encrypted[:60]}...")
else:
    print(f"    ❌ BŁĄD: {r.text}")
    exit(1)

# 5. Odszyfruj TYM SAMYM kluczem
print("\n[5] Odszyfrowanie hasła...")
print(f"    Używany klucz: {fernet_key}")
print(f"    Czy klucze są identyczne? {fernet_key == fernet_key}")

r = requests.post(f"{API_URL}/passwords/decrypt",
    json={
        "key": fernet_key,
        "password": encrypted
    },
    headers={"Authorization": f"Bearer {token}"}
)
print(f"    Status: {r.status_code}")
if r.status_code == 200:
    decrypted_password = r.json()["decrypted"]
    print(f"    ✅ Odszyfrowane: {decrypted_password}")
    
    if decrypted_password == test_password:
        print(f"\n{'='*70}")
        print("✅✅✅ TEST ZAKOŃCZONY SUKCESEM! ✅✅✅")
        print(f"{'='*70}")
    else:
        print(f"    ❌ Hasła się nie zgadzają!")
        print(f"       Oryginał: {test_password}")
        print(f"       Odszyfrowane: {decrypted_password}")
else:
    print(f"    ❌ BŁĄD: Status {r.status_code}")
    print(f"    {r.json()}")
    print(f"\n{'='*70}")
    print("❌ TEST NIEPOWODZENIE - SPRAWDŹ LOGI SERWERA ❌")
    print(f"{'='*70}")
