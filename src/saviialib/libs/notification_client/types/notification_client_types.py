from dataclasses import dataclass


@dataclass
class NotificationClientInitArgs:
    api_key: str
    channel_id: str
    client_name: str = "discord_client"


@dataclass
class ListNotificationArgs:
    pass

@dataclass
class NotifyArgs:
    content: str
    embeds: list
    files: list


@dataclass
class ReactArgs:
    notification_id: str
    emoji: str
