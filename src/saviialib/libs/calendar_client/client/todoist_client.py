from saviialib.libs.calendar_client.calendar_client_contract import (
    CalendarClientContract,
)
from saviialib.libs.calendar_client.types.calendar_client_types import (
    CreateEventArgs,
    DeleteEventArgs,
    UpdateEventArgs,
    CalendarClientInitArgs,
    GetEventByIdArgs
)
import json
from aiohttp import ClientError, ClientSession, TCPConnector, FormData
import ssl
import certifi
from saviialib.libs.log_client import LogClient, LogClientArgs, DebugArgs, LogStatus

ssl_context = ssl.create_default_context(cafile=certifi.where())

class TodoistClient(CalendarClientContract):
    def __init__(self, args: CalendarClientInitArgs) -> None:
        self.api_key = args.api_key
        self.session = ClientSession | None = None
        self.logger = LogClient(
            LogClientArgs(
                service_name="calendar_client", class_name="todoist_client"
            )
        )
    
    async def connect(self) -> None:
        if self.session:
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            
        }
        if self.api_key is None:
            raise ConnectionError("API key is not set")
        self.session = ClientSession(
            headers=headers,
            base_url="https://api.todoist.com",
            connector=TCPConnector(ssl=ssl_context),
        )

    async def close(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    
    async def create_event(self, args: CreateEventArgs) -> dict:
        self.logger.method_name = "create_event"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        url = f"/api/v10/tasks"
        try:
            payload = {
                "content": args.content,
                "priority": str(args.priority) if args.priority else None,
                "description": str(args.description) if args.description else None,
                "due_date": str(args.due_date) if args.due_date else None,
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            form = FormData()
            form.add_field(
                "payload_json", json.dumps(payload), content_type="application/json"
            )
            response = await self.session.post(url, data=form) # type: ignore
            response_json = await response.json()
            response.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return {
                "eid": response_json["id"], 
                "due_date": response_json["due"]["date"],
                "priority": response_json["priority"],
                "description": response_json["description"],
                "title": response_json["content"]
            }
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)

    
    async def update_event(self, args: UpdateEventArgs) -> dict:
        self.logger.method_name = "update_event"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        url = f"/api/v10/tasks/{args.event_id}"
        try:
            payload = {
                "content": args.content,
                "priority": str(args.priority) if args.priority else None,
                "description": str(args.description) if args.description else None,
                "due_date": str(args.due_date) if args.due_date else None,
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            form = FormData()
            form.add_field(
                "payload_json", json.dumps(payload), content_type="application/json"
            )
            response = await self.session.post(url, data=form) # type: ignore
            response.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return await response.json()
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)
    
    async def get_event_by_id(self, args: GetEventByIdArgs) -> dict:
        self.logger.method_name = "get_event_by_id"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        url = f"/api/v10/tasks/{args.event_id}"
        try:
            response = await self.session.get(url) # type: ignore
            response.raise_for_status()
            response_json = await response.json()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return {
                "eid": response_json["id"], 
                "due_date": response_json["due"]["date"],
                "priority": response_json["priority"],
                "description": response_json["description"],
                "title": response_json["content"]
            }
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)
        
    async def delete_event(self, args: DeleteEventArgs) -> None:
        self.logger.method_name = "delete_event"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        url = f"/api/v10/tasks/{args.event_id}"
        try:
            response = await self.session.delete(url) # type: ignore
            response.raise_for_status()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)
        
    async def get_events(self) -> list[dict]:
        self.logger.method_name = "get_events"
        self.logger.debug(DebugArgs(LogStatus.STARTED))
        url = f"/api/v10/tasks"
        try:
            response = await self.session.get(url) # type: ignore
            response.raise_for_status()
            response_json = await response.json()
            self.logger.debug(DebugArgs(LogStatus.SUCCESSFUL))
            return  [{
                "id": event["id"], 
                "due_date": event["due"]["date"], 
                "priority": event["priority"], 
                "description": event["description"]} for event in response_json["results"]]
        except ClientError as error:
            self.logger.debug(
                DebugArgs(LogStatus.ALERT, metadata={"error": str(error)})
            )
            raise ConnectionError(error)
        