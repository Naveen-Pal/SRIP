import smtplib
from email.message import EmailMessage
from app.config import Config


def send_email(subject, receiver, message):
    if isinstance(receiver, (list, tuple, set)):
        receiver_email = ", ".join(receiver)
    else:
        receiver_email = str(receiver)

    sender_email = Config.MAIL_USERNAME 
    app_password = Config.MAIL_PASSWORD  

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_email, app_password)
            smtp.send_message(message)
    except smtplib.SMTPException as exc:
        print(f"[EmailUtils] Failed to send mail → {exc}")
        raise

