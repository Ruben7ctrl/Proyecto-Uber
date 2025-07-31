from flask import current_app
from flask_mail import Message
from app import mail


def send_service_inquiry_email(user, extras, extras_total):
    subject = "Consulta de disponibilidad de minibús"
    recipients = [current_app.config.get("ADMIN_EMAIL")]
    body = f"Usuario: {user.name} ({user.email})\nExtras: {', '.join(e.name for e in extras)}\nTotal extras: {extras_total}"

    msg = Message(subject=subject, recipients=recipients, body=body)
    mail.send(msg)
