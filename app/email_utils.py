import os
import smtplib
import logging
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("app.email")
logger.setLevel(logging.INFO)
if not logger.handlers:
    # Uvicorn konfiguruje domyślnie tylko własne loggery - bez osobnego
    # handlera komunikaty INFO z tego loggera nie trafiłyby do konsoli serwera.
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(asctime)s [%(name)s] %(message)s"))
    logger.addHandler(_handler)
    logger.propagate = False

SMTP_HOST = os.getenv("SMTP_HOST") or None
SMTP_PORT = int(os.getenv("SMTP_PORT") or "587")
SMTP_USERNAME = os.getenv("SMTP_USERNAME") or None
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or None
SMTP_FROM = os.getenv("SMTP_FROM") or "noreply@passwordmanager.local"
SMTP_TIMEOUT_SECONDS = 10


def _send_or_log(to_email: str, subject: str, body: str) -> None:
    """Wysyła email przez SMTP, a gdy SMTP nie jest skonfigurowany - zapisuje go w logu serwera."""
    if not SMTP_HOST:
        logger.info("SMTP nieskonfigurowany - email zapisany w logu zamiast wysłania. Do=%s Temat=%s Treść=%s",
                    to_email, subject, body)
        return

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT_SECONDS) as server:
            server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, [to_email], message.as_string())
    except (smtplib.SMTPException, OSError):
        # Błąd serwera SMTP nie może przerwać żądania, które wywołało wysyłkę
        # (rejestracja, ponowne wysłanie kodu, reset hasła) - kod pozostaje ważny.
        logger.exception("Nie udało się wysłać emaila do %s (Temat=%s); kod został wygenerowany.", to_email, subject)


def send_verification_email(to_email: str, code: str) -> None:
    subject = "Weryfikacja adresu email - Menedżer Haseł"
    body = f"Twój kod weryfikacyjny: {code}\n\nKod wygasa po 24 godzinach."
    _send_or_log(to_email, subject, body)


def send_password_reset_email(to_email: str, code: str) -> None:
    subject = "Kod resetu hasła - Menedżer Haseł"
    body = f"Twój kod resetu hasła: {code}\n\nKod wygasa po 1 godzinie."
    _send_or_log(to_email, subject, body)
