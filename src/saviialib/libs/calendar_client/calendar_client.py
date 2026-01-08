from .types.calendar_client_types import (
    CreateEventArgs,
    UpdateEventArgs,
    DeleteEventArgs,
    GetEventByIdArgs,
    CalendarClientInitArgs,
)

from .client.todoist_client import TodoistClient


class CalendarClient:
    def __init__(self, args: CalendarClientInitArgs):
        clients = {
            "todoist_client": TodoistClient(args),
        }
        if clients.get(args.client_name):
            self.client_name = args.client_name
            self.client_obj = clients[args.client_name]
        else:
            raise KeyError(f"Unsupported client '{args.client_name}'.")

    async def connect(self) -> None: 
        return await self.client_obj.connect()

    async def close(self) -> None:
        return await self.client_obj.close()
    
    async def get_events(self) -> list[dict]: 
        return await self.client_obj.get_events()

    async def create_event(self, args: CreateEventArgs) -> dict:
        return await self.client_obj.create_event(args)

    async def update_event(self, args: UpdateEventArgs) -> dict:
        return await self.client_obj.update_event(args)

    async def delete_event(self, args: DeleteEventArgs) -> None:
        return await self.client_obj.delete_event(args)

    async def get_event_by_id(self, args: GetEventByIdArgs) -> dict:
        return await self.client_obj.get_event_by_id(args)
