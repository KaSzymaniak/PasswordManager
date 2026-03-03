import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite dla Replit (domyślnie) lub PostgreSQL jeśli dostępny
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./passwords.db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_user_security_columns():
    """Lightweight migration for SQLite: ensure users.fernet_key_hash exists."""
    if "sqlite" not in DATABASE_URL:
        return

    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(users)")).fetchall()
        column_names = {column[1] for column in columns}

        if "fernet_key_hash" not in column_names:
            connection.execute(text("ALTER TABLE users ADD COLUMN fernet_key_hash VARCHAR"))

# 🔑 Funkcja get_db - tego Ci brakuje!
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
