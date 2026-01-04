from abc import ABC, abstractmethod
from .types.notification_client_types import NotifyArgs, ListNotificationArgs, ReactArgs
from typing import List, Dict


class NotificationClientContract(ABC):
    @abstractmethod
    async def list_notifications(
        self, args: ListNotificationArgs
    ) -> List[Dict[str, str | int]]:
        pass

    @abstractmethod
    async def notify(self, args: NotifyArgs) -> dict:
        pass
    
    @abstractmethod
    async def react(self, args: ReactArgs) -> None:
        pass