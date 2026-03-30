from dataclasses import dataclass
from typing import Literal


@dataclass
class EmailClientInitArgs:
    """Initialization arguments for EmailClient."""

    email_address: str
    email_password: str
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587


@dataclass
class SendEmailArgs:
    """Arguments for sending an email."""

    recipient: str
    subject: str
    body: str
    content_type: Literal["plain", "html"] = "plain"
