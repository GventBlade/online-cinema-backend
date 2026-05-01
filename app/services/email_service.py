import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

class EmailService:
    @staticmethod
    def _send_email_sync(user_email: str, subject: str, html_content: str):
        message = MIMEMultipart()
        message["From"] = f"Online Cinema <{settings.SMTP_USER}>"
        message["To"] = user_email
        message["Subject"] = subject
        message.attach(MIMEText(html_content, "html"))

        try:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(message)
            print(f"📧 Email sent to {user_email}")
        except Exception as e:
            print(f"❌ Email Error: {e}")

    @staticmethod
    async def send_payment_confirmation(user_email: str, order_id: int, amount: float):
        subject = f"Order #{order_id} Confirmed - Online Cinema"
        html_content = f"""
        <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #2e7d32;">Congratulations! Payment successful✅</h2>
                    <p>Hello!</p>
                    <p>We have received your payment for order <b>#{order_id}</b>.</p>
                    <p><b>Total paid:</b> ${amount:.2f}</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p>You can now access your purchased movies in your account.</p>
                    <p>Enjoy watching!<br>Online Cinema Team</p>
                </div>
            </body>
        </html>
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, EmailService._send_email_sync, user_email, subject, html_content)

    @staticmethod
    async def send_refund_notification(user_email: str, order_id: int, amount: float):
        subject = f"Refund Confirmation: Order #{order_id}"
        html_content = f"""
        <html>
            <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
                    <h2 style="color: #d32f2f;">Refund Processed</h2>
                    <p>Hello!</p>
                    <p>We are writing to confirm that a refund has been issued for your order <b>#{order_id}</b>.</p>
                    <p><b>Refund Amount:</b> ${amount:.2f}</p>
                    <p>The funds should appear in your bank account within 3-10 business days.</p>
                    <hr style="border: 0; border-top: 1px solid #eee;">
                    <p>Best regards,<br>The Online Cinema Team</p>
                </div>
            </body>
        </html>
        """
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, EmailService._send_email_sync, user_email, subject, html_content)