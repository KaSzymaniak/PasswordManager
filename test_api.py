#!/usr/bin/env python3
"""
Test API przez faktyczne wywołania HTTP
Symuluje dokładnie to co robi użytkownik w przeglądarce
"""

import requests
import base64
import os
from cryptography.fernet import Fernet

API_URL = "http://localhost:8000"

def generate_fernet_key():
    """Generuje klucz jak JavaScript (poprawiona wersja)"""
    random_bytes = os.urandom(32)
    return base64.b64encode(random_bytes).decode()

def register_user(email, password):
    """Rejestruje użytkownika"""
    response = requests.post(f"{API_URL}/auth/register", json={
        "email": email,
        "password": password
    })
    return response

def login_user(email, password):
    """Loguje użytkownika i zwraca token"""
    response = requests.post(f"{API_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def add_password(token, service, login, password, fernet_key):
    """Dodaje hasło"""
    response = requests.post(f"{API_URL}/passwords", 
        json={
            "service": service,
            "login": login,
            "password": password,
            "key": fernet_key
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return response

def decrypt_password(token, encrypted, fernet_key):
    """Odszyfrowuje hasło"""
    response = requests.post(f"{API_URL}/passwords/decrypt",
        json={
            "key": fernet_key,
            "password": encrypted
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    return response

print("=" * 60)
print("TEST API - Szyfrowanie i Odszyfrowanie")
print("=" * 60)

# 1. Wygeneruj klucz Fernet (jak w JavaScript)
print("\n1. Generowanie klucza Fernet...")
fernet_key = generate_fernet_key()
print(f"   Klucz: {fernet_key}")
print(f"   Długość: {len(fernet_key)} znaków")

# Test czy klucz jest poprawny
try:
    f = Fernet(fernet_key.encode())
    print("   ✅ Klucz jest poprawny dla Fernet")
except Exception as e:
    print(f"   ❌ BŁĄD: Klucz niepoprawny: {e}")
    exit(1)

# 2. Rejestracja użytkownika
print("\n2. Rejestracja użytkownika...")
test_email = f"test_{os.urandom(4).hex()}@example.com"
test_password = "Test123!"
response = register_user(test_email, test_password)
if response.status_code == 200:
    print(f"   ✅ Użytkownik zarejestrowany: {test_email}")
else:
    print(f"   ℹ️  Status: {response.status_code}, {response.text}")

# 3. Logowanie
print("\n3. Logowanie...")
token = login_user(test_email, test_password)
if token:
    print(f"   ✅ Zalogowano, token: {token[:20]}...")
else:
    print(f"   ❌ Błąd logowania")
    exit(1)

# 4. Dodaj hasło (z kluczem Fernet)
print("\n4. Dodawanie hasła...")
test_service = "Facebook"
test_login = "user123"
test_plain_password = "SuperSecretPassword123!"

response = add_password(token, test_service, test_login, test_plain_password, fernet_key)
if response.status_code == 200:
    data = response.json()
    encrypted_password = data["password"]
    password_id = data["id"]
    print(f"   ✅ Hasło dodane, ID: {password_id}")
    print(f"   Zaszyfrowane hasło: {encrypted_password}")
else:
    print(f"   ❌ BŁĄD: {response.status_code}, {response.text}")
    exit(1)

# 5. Odszyfruj hasło TYM SAMYM kluczem
print("\n5. Odszyfrowanie hasła (tym samym kluczem)...")
response = decrypt_password(token, encrypted_password, fernet_key)
if response.status_code == 200:
    decrypted = response.json()["decrypted"]
    print(f"   Odszyfrowane hasło: {decrypted}")
    
    if decrypted == test_plain_password:
        print(f"   ✅ SUKCES! Hasło prawidłowo odszyfrowane!")
    else:
        print(f"   ❌ BŁĄD! Hasła się nie zgadzają!")
        print(f"      Oryginał:     {test_plain_password}")
        print(f"      Odszyfrowane: {decrypted}")
else:
    print(f"   ❌ BŁĄD: {response.status_code}")
    print(f"   {response.json()}")
    exit(1)

# 6. Test z niewłaściwym kluczem
print("\n6. Test z niewłaściwym kluczem...")
wrong_key = generate_fernet_key()
response = decrypt_password(token, encrypted_password, wrong_key)
if response.status_code == 400:
    print(f"   ✅ Właściwie odrzucono niewłaściwy klucz")
    print(f"   Komunikat: {response.json().get('detail', '')}")
else:
    print(f"   ❌ PROBLEM! Status: {response.status_code}")

print("\n" + "=" * 60)
print("TEST ZAKOŃCZONY POMYŚLNIE!")
print("=" * 60)
