from flask_mail import Message
from flask import current_app

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    with current_app.app_context():
        from app import mail
        mail.send(msg)