from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import smtplib
from dotenv import load_dotenv


def email_me(address: str, subject="Automatic Email via Python", body="Hello"):
    """
    Sends an email using the Gmail SMTP server.

    Parameters:
    - subject (str): The subject of the email. Default is "Automatic Email via Python".
    - body (str): The body of the email. Default is "Hello".
    """
    load_dotenv()
    sender = address
    recipient = sender

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_username = sender
    smtp_password = os.getenv("GAMIL")

    mime_multipart = MIMEMultipart()
    mime_multipart['from'] = sender
    mime_multipart['to'] = recipient
    mime_multipart["subject"] = subject

    email_body = MIMEText(body, 'plain', 'utf-8')
    mime_multipart.attach(email_body)

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        # Code to send the email
        smtp.ehlo()
        smtp.starttls()
        smtp.login(smtp_username, smtp_password + "py")
        smtp.send_message(mime_multipart)
        print("Email enviado com sucesso!")


if __name__ == "__main__":
    email_me()
