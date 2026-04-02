from abc import ABC, abstractmethod

from .types.email_client_types import SendEmailArgs


class EmailClientContract(ABC):
    """Abstract contract that all email client implementations must satisfy."""

    @abstractmethod
    async def send_email(self, args: SendEmailArgs) -> dict:
        """Send an email according to the provided arguments.

        :param args: SendEmailArgs containing recipient, subject, body, and content type
        :return: dict with send result metadata
        """
        pass
