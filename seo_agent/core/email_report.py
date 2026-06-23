import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_email_report(sender_email, sender_password, receiver_email, subject, body, attachments):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    for file_path in attachments:
        file_path = Path(file_path)
        if file_path.exists():
            msg.add_attachment(
                file_path.read_bytes(),
                maintype="application",
                subtype="octet-stream",
                filename=file_path.name,
            )

    with smtplib.SMTP("smtp.office365.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)