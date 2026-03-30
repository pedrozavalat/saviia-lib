from saviialib.libs.email_client.email_client_contract import EmailClientContract
from saviialib.libs.email_client.types.email_client_types import (
    EmailClientInitArgs,
    SendEmailArgs,
)
from .clients.smtplib_client import SmtpLibClient


class EmailClient(EmailClientContract):
    """Main email client that delegates sending to a concrete SMTP implementation."""

    # Registry of supported client names; extend here to add future implementations.
    CLIENTS = {"smtplib_client"}

    def __init__(self, args: EmailClientInitArgs) -> None:
        self.client_obj = SmtpLibClient(args)

    async def send_email(self, args: SendEmailArgs) -> dict:
        """Send an email using the configured SMTP client.

        :param args: SendEmailArgs with recipient, subject, body, and content_type
        :return: dict with result metadata
        """
        return await self.client_obj.send_email(args)
