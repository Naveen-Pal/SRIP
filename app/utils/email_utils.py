import smtplib
from email.message import EmailMessage
from app.config import Config

def send_email(subject,receiver_email, message):
    sender_email = Config.MAIL_USERNAME  # Your email address
    app_password = Config.MAIL_PASSWORD # App password from Gmail

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content(message)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)
        print(f"OTP sent to {receiver_email}")
        smtp.quit()
