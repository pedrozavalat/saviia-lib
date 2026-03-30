import smtplib
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from saviialib.libs.email_client import EmailClient, EmailClientInitArgs, SendEmailArgs
from saviialib.libs.email_client.clients.smtplib_client import SmtpLibClient


class TestSmtpLibClientSendEmail(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.init_args = EmailClientInitArgs(
            client_name="smtplib",
            email_address="sender@example.com",
            email_password="secret",
            smtp_server="smtp.gmail.com",
            smtp_port=587,
        )
        self.send_args_plain = SendEmailArgs(
            recipient="recipient@example.com",
            subject="Test Subject",
            body="Hello, world!",
            content_type="plain",
        )
        self.send_args_html = SendEmailArgs(
            recipient="recipient@example.com",
            subject="Test Subject",
            body="<h1>Hello</h1>",
            content_type="html",
        )

    @patch("saviialib.libs.email_client.clients.smtplib_client.smtplib.SMTP")
    async def test_should_send_plain_email_successfully(self, mock_smtp_class):
        # Arrange
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)
        client = SmtpLibClient(self.init_args)

        # Act
        result = await client.send_email(self.send_args_plain)

        # Assert
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("sender@example.com", "secret")
        mock_server.sendmail.assert_called_once()
        self.assertEqual(result["recipient"], "recipient@example.com")
        self.assertEqual(result["subject"], "Test Subject")
        self.assertEqual(result["content_type"], "plain")
        self.assertEqual(result["status"], "sent")

    @patch("saviialib.libs.email_client.clients.smtplib_client.smtplib.SMTP")
    async def test_should_send_html_email_successfully(self, mock_smtp_class):
        # Arrange
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)
        client = SmtpLibClient(self.init_args)

        # Act
        result = await client.send_email(self.send_args_html)

        # Assert
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("sender@example.com", "secret")
        mock_server.sendmail.assert_called_once()
        self.assertEqual(result["content_type"], "html")
        self.assertEqual(result["status"], "sent")

    @patch("saviialib.libs.email_client.clients.smtplib_client.smtplib.SMTP")
    async def test_should_raise_connection_error_on_smtp_exception(
        self, mock_smtp_class
    ):
        # Arrange
        mock_smtp_class.side_effect = smtplib.SMTPException("SMTP failure")
        client = SmtpLibClient(self.init_args)

        # Act & Assert
        with self.assertRaises(ConnectionError) as context:
            await client.send_email(self.send_args_plain)
        self.assertIn("SMTP failure", str(context.exception))


class TestEmailClientSendEmail(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.init_args = EmailClientInitArgs(
            email_address="sender@example.com",
            email_password="secret",
            client_name="smtplib",
        )
        self.send_args = SendEmailArgs(
            recipient="recipient@example.com",
            subject="Hello",
            body="Test body",
            content_type="plain",
        )

    @patch(
        "saviialib.libs.email_client.email_client.SmtpLibClient.send_email",
        new_callable=AsyncMock,
    )
    async def test_should_delegate_send_email_to_smtplib_client(self, mock_send_email):
        # Arrange
        expected = {
            "recipient": "recipient@example.com",
            "subject": "Hello",
            "content_type": "plain",
            "status": "sent",
        }
        mock_send_email.return_value = expected
        client = EmailClient(self.init_args)

        # Act
        result = await client.send_email(self.send_args)

        # Assert
        mock_send_email.assert_called_once_with(self.send_args)
        self.assertEqual(result, expected)

    def test_should_use_default_smtp_server_and_port(self):
        # Arrange
        args = EmailClientInitArgs(
            client_name="smtplib",
            email_address="a@b.com",
            email_password="pw",
        )
        # Act
        client = EmailClient(args)
        # Assert
        self.assertEqual(client.client_obj.smtp_server, "smtp.gmail.com")
        self.assertEqual(client.client_obj.smtp_port, 587)
