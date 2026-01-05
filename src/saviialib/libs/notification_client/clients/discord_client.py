from typing import Dict, List
from saviialib.libs.notification_client.notification_client_contract import (
    NotificationClientContract,
)
from saviialib.libs.notification_client.types.notification_client_types import (
    UpdateNotificationArgs,
    NotifyArgs,
    NotificationClientInitArgs,
    ReactArgs,
    FindNotificationArgs,
    DeleteReactionArgs,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.files_client import FilesClient, FilesClientInitArgs, ReadArgs
from saviialib.libs.log_client import LogClient, LogClientArgs, DebugArgs, LogStatus
from aiohttp import ClientError, ClientSession, TCPConnector, FormData
import ssl
import certifi
import json
import re

ssl_context = ssl.create_default_context(cafile=certifi.where())


class DiscordClient(NotificationClientContract):
    def __init__(self, args: NotificationClientInitArgs) -> None:
        self.api_key = args.api_key
        self.channel_id = args.channel_id
        self.session: ClientSession | None = None
        self.dir_client = DirectoryClient(DirectoryClientArgs("os_client"))
        self.files_client = FilesClient(FilesClientInitArgs("aiofiles_client"))
        self.logger = LogClient(
            LogClientArgs(
                service_name="notification_client", class_name="discord_client"
            )
        )

    async def connect(self) -> None:
        if self.session:
            return

        headers = {
            "Authorization": f"Bot {self.api_key}",
            
        }
        if self.api_key is None:
            raise ConnectionError("API key is not set")
        elif self.channel_id is None:
            raise ConnectionError("Channel ID is not set")
        self.session = ClientSession(
            headers=headers,
            base_url="https://discord.com",
            connector=TCPConnector(ssl=ssl_context),
        )

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def list_notifications(self) -> List[Dict[str, str | int]]:
        self.logger.method_name = "list_notifications"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        try:
            url = f"/api/v10/channels/{self.channel_id}/messages"
            response = await self.session.get(url)  # type: ignore
            response.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return await response.json()
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)

    async def find_notification(self, args: FindNotificationArgs) -> dict:
        """Returns the first notification that matches the content and reactions criteria.

        :param args: FindNotificationArgs
        :return: JSON dict of the found notification or empty dict if none found
        :rtype: dict
        """
        self.logger.method_name = "find_notification"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        try:
            notifications = await self.list_notifications()
            matches = []
            for notification in notifications:
                if re.search(args.content, notification["content"]):  # type: ignore
                    reactions = notification.get("reactions", [])
                    if not args.reactions:
                        matches.append(notification)
                    else:
                        if any(
                            reaction["emoji"]["name"] in args.reactions
                            for reaction in reactions  # type: ignore
                        ):
                            matches.append(notification)
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return matches[0] if matches else {}

        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)

    async def update_notification(self, args: UpdateNotificationArgs) -> dict:
        self.logger.method_name = "update_notification"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        try:
            notification = await self.find_notification(
                FindNotificationArgs(content=args.notification_title)
            )
            if not notification:
                raise ClientError(
                    f"Notification with content '{args.notification_title}' doesn't exist."
                )

            nid = notification["id"]
            url = f"/api/v10/channels/{self.channel_id}/messages/{nid}"
            payload = {"content": args.new_content}
            response = await self.session.patch(url, json=payload)  # type: ignore
            response.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return await response.json()
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)

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
            attachments = []
            for idx, file_path in enumerate(args.files):
                filename = self.dir_client.get_basename(file_path)
                attachments.append(
                    {
                        "id": idx,
                        "filename": filename,
                    }
                )
            payload["embeds"] = args.embeds  # type: ignore
            payload["attachments"] = attachments  # type: ignore

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
            new_notification = await self.session.post(url, data=form)  # type: ignore
            new_notification.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return await new_notification.json()
            # Supress embeds
            # nid = new_notification_json["id"]
            # url += f"/{nid}"
            # notification_updated = await self.session.patch(url, json={"flags": 4}) # type: ignore
            # notification_updated.raise_for_status()
            # return await notification_updated.json()
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)

    async def react(self, args: ReactArgs) -> dict:
        self.logger.method_name = "react"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        try:
            url = f"/api/v10/channels/{self.channel_id}/messages/{args.notification_id}/reactions/{args.emoji}/@me"
            response = await self.session.put(url)  # type: ignore
            response.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return await response.json()
        except ClientError as error:
            if error.status == 204:  # type: ignore
                self.logger.debug(DebugArgs(LogStatus.ALERT))
                return {}
            raise ConnectionError(error)

    async def delete_reaction(self, args: DeleteReactionArgs) -> dict:
        self.logger.method_name = "react"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        try:
            url = f"/api/v10/channels/{self.channel_id}/messages/{args.notification_id}/reactions/{args.emoji}/@me"
            response = await self.session.delete(url)  # type: ignore
            response.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return await response.json()
        except ClientError as error:
            if error.status == 204:  # type: ignore
                self.logger.debug(
                    DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
                )
                return {}
            raise ConnectionError(error)
