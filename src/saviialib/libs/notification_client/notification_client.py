from typing import Dict, List

from saviialib.libs.notification_client.types.notification_client_types import (
    FindNotificationArgs,
    ReactArgs,
)
from .notification_client_contract import NotificationClientContract
from .types.notification_client_types import (
    NotifyArgs,
    NotificationClientInitArgs,
    UpdateNotificationArgs,
    DeleteReactionArgs
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

    async def connect(self) -> None:
        return await self.client_obj.connect()

    async def close(self) -> None:
        return await self.client_obj.close()

    async def notify(self, args: NotifyArgs) -> dict:
        return await self.client_obj.notify(args)

    async def list_notifications(self) -> List[Dict[str, str | int]]:
        return await self.client_obj.list_notifications()

    async def react(self, args: ReactArgs) -> dict:
        return await self.client_obj.react(args)

    async def find_notification(self, args: FindNotificationArgs) -> dict:
        return await self.client_obj.find_notification(args)

    async def update_notification(self, args: UpdateNotificationArgs) -> dict:
        return await self.client_obj.update_notification(args)

    async def delete_reaction(self, args: DeleteReactionArgs) -> dict:
        return await self.client_obj.delete_reaction(args)