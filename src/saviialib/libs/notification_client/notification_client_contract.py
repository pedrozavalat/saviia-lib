from abc import ABC, abstractmethod
from typing import List, Dict
from .types.notification_client_types import (
    NotifyArgs,
    ReactArgs,
    FindNotificationArgs,
    UpdateNotificationArgs,
    DeleteReactionArgs
)


class NotificationClientContract(ABC):
    @abstractmethod
    async def list_notifications(self) -> List[Dict[str, str | int]]:
        pass

    @abstractmethod
    async def notify(self, args: NotifyArgs) -> dict:
        pass

    @abstractmethod
    async def react(self, args: ReactArgs) -> dict:
        pass

    @abstractmethod
    async def find_notification(self, args: FindNotificationArgs) -> dict:
        pass

    @abstractmethod
    async def update_notification(self, args: UpdateNotificationArgs) -> dict:
        pass
    
    @abstractmethod
    async def delete_reaction(self, args: DeleteReactionArgs) -> dict:
        pass
    

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass
