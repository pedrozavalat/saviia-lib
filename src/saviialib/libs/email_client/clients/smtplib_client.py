import asyncio
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from saviialib.libs.email_client.email_client_contract import EmailClientContract
from saviialib.libs.email_client.types.email_client_types import (
    EmailClientInitArgs,
    SendEmailArgs,
)
from saviialib.libs.log_client import LogClient, LogClientArgs, DebugArgs, LogStatus


class SmtpLibClient(EmailClientContract):
    """Concrete email client implementation using Python's smtplib."""

    def __init__(self, args: EmailClientInitArgs) -> None:
        self.email_address = args.email_address
        self.email_password = args.email_password
        self.smtp_server = args.smtp_server
        self.smtp_port = args.smtp_port
        self.logger = LogClient(
            LogClientArgs(service_name="email_client", class_name="smtplib_client")
        )

    async def send_email(self, args: SendEmailArgs) -> dict:
        """Send an email via SMTP using starttls and login.

        :param args: SendEmailArgs with recipient, subject, body, and content_type
        :return: dict with result metadata
        :raises ConnectionError: if the SMTP connection or send operation fails
        """
        self.logger.method_name = "send_email"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self._send_sync, args
            )
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return result
        except smtplib.SMTPException as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(str(error)) from error

    def _send_sync(self, args: SendEmailArgs) -> dict:
        """Perform the synchronous SMTP send operation.

        :param args: SendEmailArgs
        :return: dict with result metadata
        """
        message = MIMEMultipart()
        message["From"] = self.email_address
        message["To"] = args.recipient
        message["Subject"] = args.subject
        message.attach(MIMEText(args.body, args.content_type))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.email_address, self.email_password)
            server.sendmail(self.email_address, args.recipient, message.as_string())

        return {
            "recipient": args.recipient,
            "subject": args.subject,
            "content_type": args.content_type,
            "status": "sent",
        }
