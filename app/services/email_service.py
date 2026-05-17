import smtplib
from email.message import EmailMessage
from app.core.config import settings
from app.core.celery_app import celery_app  # Імпортуємо наш Celery


class EmailService:
    @staticmethod
    @celery_app.task(name="send_payment_email_task")  # Робимо функцію фоновим завданням
    def send_payment_confirmation(user_email: str, order_id: int, amount: float):
        """
        Фонова задача для відправки підтвердження оплати.
        """
        msg = EmailMessage()
        msg.set_content(
            f"Thank you! Your payment for order #{order_id} in the amount of ${amount} was successful."
        )
        msg["Subject"] = "Payment Confirmation - Online Cinema"
        msg["From"] = settings.SMTP_USER
        msg["To"] = user_email

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            return f"Email sent to {user_email}"
        except Exception as e:
            return f"Failed to send email: {str(e)}"

    @staticmethod
    @celery_app.task(name="send_refund_email_task")
    def send_refund_notification(user_email: str, order_id: int, amount: float):
        """
        Фонова задача для відправки сповіщення про повернення коштів.
        """
        msg = EmailMessage()
        msg.set_content(
            f"Your refund for order #{order_id} in the amount of ${amount} has been processed."
        )
        msg["Subject"] = "Refund Processed - Online Cinema"
        msg["From"] = settings.SMTP_USER
        msg["To"] = user_email

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
            return f"Refund email sent to {user_email}"
        except Exception as e:
            return f"Failed to send refund email: {str(e)}"
