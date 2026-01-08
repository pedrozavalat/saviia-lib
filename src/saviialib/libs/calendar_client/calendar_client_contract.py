from abc import abstractmethod, ABC
from .types.calendar_client_types import (
    CreateEventArgs,
    UpdateEventArgs,
    DeleteEventArgs,
    GetEventByIdArgs,
)


class CalendarClientContract(ABC):
    @abstractmethod
    async def create_event(self, args: CreateEventArgs) -> dict:
        pass

    @abstractmethod
    async def update_event(self, args: UpdateEventArgs) -> dict:
        pass

    @abstractmethod
    async def delete_event(self, args: DeleteEventArgs) -> None:
        pass

    @abstractmethod
    async def get_event_by_id(self, args: GetEventByIdArgs) -> dict:
        pass

    @abstractmethod
    async def get_events(self) -> list[dict]:
        pass

    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass
