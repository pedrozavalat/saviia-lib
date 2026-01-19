from dataclasses import dataclass, field


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


@dataclass
class FindNotificationArgs:
    content: str
    reactions: list = field(default_factory=list)


@dataclass
class UpdateNotificationArgs:
    notification_title: str
    new_content: str


@dataclass
class DeleteReactionArgs:
    notification_id: str
    emoji: str
