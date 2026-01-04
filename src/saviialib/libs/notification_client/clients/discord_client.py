from typing import Dict, List
from saviialib.libs.notification_client.notification_client_contract import (
    NotificationClientContract,
)
from saviialib.libs.notification_client.types.notification_client_types import (
    ListNotificationArgs,
    NotifyArgs,
    NotificationClientInitArgs,
    ReactArgs,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs, ReadArgs
from saviialib.libs.log_client import LogClient, LogClientArgs, DebugArgs, LogStatus
from aiohttp import ClientError, ClientSession, TCPConnector, FormData
import ssl
import certifi
import json

ssl_context = ssl.create_default_context(cafile=certifi.where())


class DiscordClient(NotificationClientContract):
    def __init__(self, args: NotificationClientInitArgs) -> None:
        self.api_key = args.api_key
        self.channel_id = args.channel_id
        self.session = None
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))
        self.files_client = FilesClient(FilesClientInitArgs("aiofiles_client"))
        self.logger = LogClient(
            LogClientArgs(
                service_name="notification_client", class_name="discord_client"
            )
        )

    async def __aenter__(self):
        try:
            headers = {
                "Authorization": f"Bot {self.api_key}",
                "Content-Type": "application/json",
            }
            base_url = "https://discord.com"
            self.session = ClientSession(
                headers=headers,
                base_url=base_url,
                connector=TCPConnector(ssl=ssl_context),
            )
            if self.api_key is None:
                raise ConnectionError("API key is not set")
            elif self.channel_id is None:
                raise ConnectionError("Channel ID is not set")
            return self
        except ClientError as error:
            raise ConnectionError(error)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()  # type:ignore

    async def list_notifications(
        self, args: ListNotificationArgs
    ) -> List[Dict[str, str | int]]:
        return await super().list_notifications(args)

    async def notify(self, args: NotifyArgs) -> dict:
        self.logger.method_name = "notify"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        try:
            url = f"/api/v10/channels/{self.channel_id}/messages"
            payload = {
                "content": args.content,
            }
            if args.embeds:
                payload["embeds"] = args.embeds  # type: ignore
            # No files
            if not args.files:
                response = await self.session.post(url, json=payload)  # type: ignore
                response.raise_for_status()
                return await response.json()
            # Multi-part
            form = FormData()
            form.add_field(
                "payload_json", json.dumps(payload), content_type="application/json"
            )
            for idx, file_path in enumerate(args.files):
                file = await self.files_client.read(ReadArgs(file_path, "rb"))
                form.add_field(
                    f"files[{idx}]",
                    file,
                    filename=self.dir_client.get_basename(file_path),
                    content_type="image/jpeg",
                )
            response = await self.session.post(url, data=form)  # type: ignore
            response.raise_for_status()
            return await response.json()
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)

    async def react(self, args: ReactArgs) -> None:
        try:
            url = f"/api/v10/channels/{self.channel_id}/messages/{args.notification_id}/reactions/{args.emoji}/@me"
            response = await self.session.put(url)  # type: ignore
            response.raise_for_status()
            response_json = await response.json()
            return response_json
        except ClientError as error:
            if error.status == 204: # type: ignore
                return 
            raise ConnectionError(error)
