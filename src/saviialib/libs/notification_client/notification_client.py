from typing import Dict, List

from saviialib.libs.notification_client.types.notification_client_types import ReactArgs
from .notification_client_contract import NotificationClientContract
from .types.notification_client_types import (
    NotifyArgs,
    NotificationClientInitArgs,
    ListNotificationArgs,
)
from .clients.discord_client import DiscordClient


class NotificationClient(NotificationClientContract):
    CLIENTS = {"discord_client"}

    def __init__(self, args: NotificationClientInitArgs) -> None:
        if args.client_name not in NotificationClient.CLIENTS:
            msg = f"Unsupported client {args.client_name}"
            raise KeyError(msg)
        if args.client_name == "discord_client":
            self.client_obj = DiscordClient(args)
        self.client_name = args.client_name

    async def __aenter__(self):
        return await self.client_obj.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client_obj.__aexit__(exc_type, exc_val, exc_tb)

    async def notify(self, args: NotifyArgs) -> dict:
        return await self.client_obj.notify(args)

    async def list_notifications(
        self, args: ListNotificationArgs
    ) -> List[Dict[str, str | int]]:
        return await self.client_obj.list_notifications(args)

    async def react(self, args: ReactArgs) -> None:
        return await self.client_obj.react(args)
