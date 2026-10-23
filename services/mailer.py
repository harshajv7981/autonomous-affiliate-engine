from __future__ import annotations

import smtplib
from email.message import EmailMessage


class SmtpMailer:
    """Plain SMTP with STARTTLS (e.g. Gmail + app password). Standard library only."""

    def __init__(self, host: str, port: int, username: str, password: str, from_header: str):
        self.host, self.port = host, port
        self.username, self.password = username, password
        self.from_header = from_header

    def send(self, to: str, subject: str, text: str, html: str, headers: dict[str, str]) -> None:
        message = EmailMessage()
        message["From"] = self.from_header
        message["To"] = to
        message["Subject"] = subject
        for name, value in headers.items():
            message[name] = value
        message.set_content(text)
        message.add_alternative(html, subtype="html")
        with smtplib.SMTP(self.host, self.port, timeout=30) as smtp:
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.send_message(message)
