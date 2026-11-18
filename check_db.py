"""Podgląd zawartości lokalnej bazy SQLite (tabele, liczba wierszy, przykładowe wpisy)."""
import sqlite3
import os

db_path = "passwords.db"

if os.path.exists(db_path):
    print(f"Baza danych istnieje: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"\nTabele w bazie: {[t[0] for t in tables]}")

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  {table_name}: {count} wierszy")

            # Hasła są przechowywane jako szyfrogramy, więc podgląd jest bezpieczny
            if count > 0 and 'password' in table_name.lower():
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                for row in cursor.fetchall():
                    print(f"    {row}")
    except Exception as e:
        print(f"Błąd: {e}")

    conn.close()
else:
    print(f"Baza danych nie istnieje: {db_path}")
