import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_otp_email(to_email: str, otp: str) -> None:
    subject = "Your AI QA Analyzer OTP Code"
    body = (
        f"Your OTP code is: {otp}\n\n"
        f"This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.\n"
        "If you did not request this code, you can ignore this email."
    )

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT,
            timeout=15,
        ) as smtp:
            if settings.SMTP_STARTTLS:
                smtp.starttls()

            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(msg)

        logger.info("OTP email sent to %s", to_email)
        print(f"[OTP EMAIL SENT] Email: {to_email} | OTP: {otp}")

    except Exception as exc:
        logger.exception("Failed to send OTP email to %s: %s", to_email, exc)
        print(f"[DEV OTP FALLBACK] Email: {to_email} | OTP: {otp}")