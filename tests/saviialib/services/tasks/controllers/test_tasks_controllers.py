import sys
import types
from unittest.mock import AsyncMock, patch

import pytest

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    setattr(pandas_stub, "DataFrame", type("DataFrame", (), {}))
    setattr(pandas_stub, "Series", type("Series", (), {}))
    setattr(pandas_stub, "read_csv", lambda *args, **kwargs: None)
    sys.modules["pandas"] = pandas_stub
if "numpy" not in sys.modules:
    sys.modules["numpy"] = types.ModuleType("numpy")

from saviialib.general_types.api.saviia_tasks_api_types import SaviiaTasksConfig
from saviialib.services.tasks.controllers.create_task import CreateTaskController
from saviialib.services.tasks.controllers.delete_task import DeleteTaskController
from saviialib.services.tasks.controllers.get_pending_tasks import (
    GetPendingTasksController,
)
from saviialib.services.tasks.controllers.get_tasks import GetTasksController
from saviialib.services.tasks.controllers.types.create_task_types import (
    CreateTaskControllerInput,
)
from saviialib.services.tasks.controllers.types.delete_task_types import (
    DeleteTaskControllerInput,
)
from saviialib.services.tasks.controllers.types.get_pending_tasks_types import (
    GetPendingTasksControllerInput,
)
from saviialib.services.tasks.controllers.types.get_tasks_types import (
    GetTasksControllerInput,
)
from saviialib.services.tasks.controllers.types.update_task_types import (
    UpdateTaskControllerInput,
)
from saviialib.services.tasks.controllers.update_task import UpdateTaskController
from saviialib.services.tasks.use_cases.types.create_task_types import (
    CreateTaskUseCaseOutput,
)
from saviialib.services.tasks.use_cases.types.delete_task_types import (
    DeleteTaskUseCaseOutput,
)
from saviialib.services.tasks.use_cases.types.get_pending_tasks_types import (
    GetPendingTasksUseCaseOutput,
)
from saviialib.services.tasks.use_cases.types.get_tasks_types import (
    GetTasksUseCaseOutput,
)
from saviialib.services.tasks.use_cases.types.update_task_types import (
    UpdateTaskUseCaseOutput,
)


@pytest.fixture
def tasks_config() -> SaviiaTasksConfig:
    return SaviiaTasksConfig(
        bot_token="token",
        task_channel_id="channel",
        email_address="mail@test.com",
        email_password="password",
        local_backup_path="/tmp",
    )


@pytest.mark.asyncio
@patch("saviialib.services.tasks.controllers.create_task.CreateTaskValidator")
@patch("saviialib.services.tasks.controllers.create_task.CreateTaskUseCase")
@patch("saviialib.services.tasks.controllers.create_task.NotificationClient")
@patch("saviialib.services.tasks.controllers.create_task.EmailClient")
@patch("saviialib.services.tasks.controllers.create_task.LogClient")
async def test_create_task_controller_should_delegate(
    mock_log_client_class,
    mock_email_client_class,
    mock_notification_client_class,
    mock_use_case_class,
    mock_validator_class,
    tasks_config,
):
    mock_notification_client = mock_notification_client_class.return_value
    mock_notification_client.connect = AsyncMock(return_value=None)
    mock_notification_client.close = AsyncMock(return_value=None)
    mock_validator = mock_validator_class.return_value
    mock_validator.validate.return_value = None
    mock_use_case_instance = mock_use_case_class.return_value
    mock_use_case_instance.execute = AsyncMock(
        return_value=CreateTaskUseCaseOutput(task_id="task-1")
    )

    controller = CreateTaskController(
        CreateTaskControllerInput(
            task={"title": "task"},
            images=[],
            config=tasks_config,
        )
    )

    result = await controller.execute()

    assert result.message == "Task created successfully!"
    assert result.status == 200
    assert result.metadata == {"task_id": "task-1"}
    mock_notification_client.connect.assert_awaited_once()
    mock_notification_client.close.assert_awaited_once()
    mock_use_case_instance.execute.assert_awaited_once()
    assert mock_email_client_class.called
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.tasks.controllers.update_task.UpdateTaskValidator")
@patch("saviialib.services.tasks.controllers.update_task.UpdateTaskUseCase")
@patch("saviialib.services.tasks.controllers.update_task.NotificationClient")
@patch("saviialib.services.tasks.controllers.update_task.EmailClient")
@patch("saviialib.services.tasks.controllers.update_task.LogClient")
async def test_update_task_controller_should_delegate(
    mock_log_client_class,
    mock_email_client_class,
    mock_notification_client_class,
    mock_use_case_class,
    mock_validator_class,
    tasks_config,
):
    mock_notification_client = mock_notification_client_class.return_value
    mock_notification_client.connect = AsyncMock(return_value=None)
    mock_notification_client.close = AsyncMock(return_value=None)
    mock_validator = mock_validator_class.return_value
    mock_validator.validate.return_value = None
    mock_use_case_instance = mock_use_case_class.return_value
    mock_use_case_instance.execute = AsyncMock(
        return_value=UpdateTaskUseCaseOutput(
            tid="1",
            title="task",
            deadline="2026-01-01",
            creation="2025-12-01",
            priority=1,
            description="desc",
            periodicity="daily",
            assignee="user",
            category="cat",
            completed=True,
        )
    )

    controller = UpdateTaskController(
        UpdateTaskControllerInput(
            task={
                "tid": "1",
                "title": "task",
                "deadline": "2026-01-01",
                "creation": "2025-12-01",
                "execution": "2026-01-02",
                "priority": 1,
                "description": "desc",
                "periodicity": "daily",
                "assignee": "user",
                "category": "cat",
            },
            completed=True,
            config=tasks_config,
        )
    )

    result = await controller.execute()

    assert result.message == "Task updated successfully!"
    assert result.status == 200
    assert result.metadata["tid"] == "1"
    mock_notification_client.connect.assert_awaited_once()
    mock_notification_client.close.assert_awaited_once()
    mock_use_case_instance.execute.assert_awaited_once()
    assert mock_email_client_class.called
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.tasks.controllers.delete_task.SchemaValidatorClient")
@patch("saviialib.services.tasks.controllers.delete_task.DeleteTaskUseCase")
@patch("saviialib.services.tasks.controllers.delete_task.NotificationClient")
@patch("saviialib.services.tasks.controllers.delete_task.LogClient")
async def test_delete_task_controller_should_delegate(
    mock_log_client_class,
    mock_notification_client_class,
    mock_use_case_class,
    mock_schema_validator_class,
    tasks_config,
):
    mock_notification_client = mock_notification_client_class.return_value
    mock_notification_client.connect = AsyncMock(return_value=None)
    mock_notification_client.close = AsyncMock(return_value=None)
    mock_schema_validator = mock_schema_validator_class.return_value
    mock_schema_validator.validate.return_value = None
    mock_use_case_instance = mock_use_case_class.return_value
    mock_use_case_instance.execute = AsyncMock(
        return_value=DeleteTaskUseCaseOutput(task_id="1")
    )

    controller = DeleteTaskController(
        DeleteTaskControllerInput(task_id="1", config=tasks_config)
    )

    result = await controller.execute()

    assert result.message == "Task deleted successfully!"
    assert result.status == 200
    assert result.metadata == {"task_id": "1"}
    mock_notification_client.connect.assert_awaited_once()
    mock_notification_client.close.assert_awaited_once()
    mock_use_case_instance.execute.assert_awaited_once()
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.tasks.controllers.get_tasks.SchemaValidatorClient")
@patch("saviialib.services.tasks.controllers.get_tasks.GetTasksUseCase")
@patch("saviialib.services.tasks.controllers.get_tasks.NotificationClient")
async def test_get_tasks_controller_should_delegate(
    mock_notification_client_class,
    mock_use_case_class,
    mock_schema_validator_class,
    tasks_config,
):
    mock_notification_client = mock_notification_client_class.return_value
    mock_notification_client.connect = AsyncMock(return_value=None)
    mock_notification_client.close = AsyncMock(return_value=None)
    mock_schema_validator = mock_schema_validator_class.return_value
    mock_schema_validator.validate.return_value = None
    mock_use_case_instance = mock_use_case_class.return_value
    mock_use_case_instance.execute = AsyncMock(
        return_value=GetTasksUseCaseOutput(tasks=[{"task_id": "1"}])
    )

    controller = GetTasksController(
        GetTasksControllerInput(config=tasks_config, params={"completed": False})
    )

    result = await controller.execute()

    assert result.message == "The service works operates successfully"
    assert result.status == 200
    assert result.metadata == {"tasks": [{"task_id": "1"}]}
    mock_notification_client.connect.assert_awaited_once()
    mock_notification_client.close.assert_awaited_once()
    mock_use_case_instance.execute.assert_awaited_once()


@pytest.mark.asyncio
@patch("saviialib.services.tasks.controllers.get_pending_tasks.SchemaValidatorClient")
@patch("saviialib.services.tasks.controllers.get_pending_tasks.GetPendingTasksUseCase")
@patch("saviialib.services.tasks.controllers.get_pending_tasks.NotificationClient")
@patch("saviialib.services.tasks.controllers.get_pending_tasks.EmailClient")
@patch("saviialib.services.tasks.controllers.get_pending_tasks.DirectoryClient")
async def test_get_pending_tasks_controller_should_delegate(
    mock_directory_client_class,
    mock_email_client_class,
    mock_notification_client_class,
    mock_use_case_class,
    mock_schema_validator_class,
    tasks_config,
):
    mock_notification_client = mock_notification_client_class.return_value
    mock_notification_client.connect = AsyncMock(return_value=None)
    mock_notification_client.close = AsyncMock(return_value=None)
    mock_schema_validator = mock_schema_validator_class.return_value
    mock_schema_validator.validate.return_value = None
    mock_use_case_instance = mock_use_case_class.return_value
    mock_use_case_instance.execute = AsyncMock(
        return_value=GetPendingTasksUseCaseOutput(
            overdue=[{"task_id": "1"}], ontime=[{"task_id": "2"}]
        )
    )

    controller = GetPendingTasksController(
        GetPendingTasksControllerInput(config=tasks_config, download=True, notify=True)
    )

    result = await controller.execute()

    assert result.message == "The pending tasks have been successfully extracted."
    assert result.status == 200
    assert result.metadata == {
        "overdue": [{"task_id": "1"}],
        "ontime": [{"task_id": "2"}],
    }
    mock_notification_client.connect.assert_awaited_once()
    mock_notification_client.close.assert_awaited_once()
    mock_use_case_instance.execute.assert_awaited_once()
    assert mock_email_client_class.called
    assert mock_directory_client_class.called
