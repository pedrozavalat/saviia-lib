from saviialib.libs.email_client.email_client_contract import EmailClientContract
from saviialib.libs.email_client.types.email_client_types import (
    EmailClientInitArgs,
    SendEmailArgs,
)
from .clients.smtplib_client import SmtpLibClient


class EmailClient(EmailClientContract):
    """Main email client that delegates sending to a concrete SMTP implementation."""

    # Registry of supported client names; extend here to add future implementations.
    CLIENTS = {"smtplib"}

    def __init__(self, args: EmailClientInitArgs) -> None:
        self.client_obj = SmtpLibClient(args)
        if args.client_name not in EmailClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        if args.client_name == "smtplib":
            self.client_obj = SmtpLibClient(args)
        self.client_name = args.client_name

    async def send_email(self, args: SendEmailArgs) -> dict:
        """Send an email using the configured SMTP client.

        :param args: SendEmailArgs with recipient, subject, body, and content_type
        :return: dict with result metadata
        """
        return await self.client_obj.send_email(args)
