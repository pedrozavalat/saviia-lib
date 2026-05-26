import sys
import types
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

if "pandas" not in sys.modules:
    pandas_stub = types.ModuleType("pandas")
    setattr(pandas_stub, "DataFrame", type("DataFrame", (), {}))
    setattr(pandas_stub, "Series", type("Series", (), {}))
    setattr(pandas_stub, "read_csv", lambda *args, **kwargs: None)
    sys.modules["pandas"] = pandas_stub
if "numpy" not in sys.modules:
    sys.modules["numpy"] = types.ModuleType("numpy")

from saviialib.services.tasks.entities.task import SaviiaTask
from saviialib.services.tasks.use_cases.create_task import CreateTaskUseCase
from saviialib.services.tasks.use_cases.delete_task import DeleteTaskUseCase
from saviialib.services.tasks.use_cases.get_pending_tasks import GetPendingTasksUseCase
from saviialib.services.tasks.use_cases.get_tasks import GetTasksUseCase
from saviialib.services.tasks.use_cases.types.create_task_types import (
    CreateTaskUseCaseInput,
)
from saviialib.services.tasks.use_cases.types.delete_task_types import (
    DeleteTaskUseCaseInput,
)
from saviialib.services.tasks.use_cases.types.get_pending_tasks_types import (
    GetPendingTasksUseCaseInput,
)
from saviialib.services.tasks.use_cases.types.get_tasks_types import (
    GetTasksUseCaseInput,
)
from saviialib.services.tasks.use_cases.types.update_task_types import (
    UpdateTaskUseCaseInput,
)
from saviialib.services.tasks.use_cases.update_task import UpdateTaskUseCase


@pytest.mark.asyncio
@patch("saviialib.services.tasks.use_cases.create_task.LogClient")
@patch("saviialib.services.tasks.use_cases.create_task.DirectoryClient")
@patch("saviialib.services.tasks.use_cases.create_task.FilesClient")
async def test_create_task_use_case_should_send_notification_and_email(
    mock_files_client_class,
    mock_directory_client_class,
    mock_log_client_class,
):
    notification_client = MagicMock()
    notification_client.notify = AsyncMock(return_value={"id": "task-1"})
    notification_client.react = AsyncMock(return_value=None)
    email_client = MagicMock()
    email_client.send_email = AsyncMock(return_value=None)
    directory_client = mock_directory_client_class.return_value
    directory_client.makedirs = AsyncMock(return_value=None)
    directory_client.removedirs = AsyncMock(return_value=None)
    files_client = mock_files_client_class.return_value
    files_client.write = AsyncMock(return_value=None)

    use_case = CreateTaskUseCase(
        CreateTaskUseCaseInput(
            task=SaviiaTask(
                title="task",
                deadline="2026-01-01",
                creation="2025-12-01",
                priority=1,
                assignee="user",
                completed=False,
                execution="",
                assignee_email="user@test.com",
                assignee_discord_username="user",
                tid="",
                description="desc",
                periodicity="daily",
                category="cat",
                images=[{"name": "img.jpg", "data": b"bytes"}],
            ),
            notification_client=notification_client,
            email_client=email_client,
        )
    )

    result = await use_case.execute()

    assert result.task_id == "task-1"
    notification_client.notify.assert_awaited_once()
    notification_client.react.assert_awaited_once()
    email_client.send_email.assert_awaited_once()
    directory_client.makedirs.assert_awaited_once_with("tmp")
    directory_client.removedirs.assert_awaited_once_with("tmp")
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.tasks.use_cases.update_task.LogClient")
async def test_update_task_use_case_should_update_notification(mock_log_client_class):
    notification_client = MagicMock()
    notification_client.find_notification = AsyncMock(
        return_value={
            "content": "## task\n__Estado__: Pendiente\n__Fecha limite__: 2026-01-01\n__Fecha creación__: 2025-12-01\n__Prioridad__: 1\n",
        }
    )
    notification_client.update_notification = AsyncMock(return_value=None)
    notification_client.react = AsyncMock(return_value=None)
    notification_client.delete_reaction = AsyncMock(return_value=None)
    email_client = MagicMock()
    email_client.send_email = AsyncMock(return_value=None)

    use_case = UpdateTaskUseCase(
        UpdateTaskUseCaseInput(
            task=SaviiaTask(
                tid="1",
                title="task",
                deadline="2026-01-01",
                creation="2025-12-01",
                priority=1,
                assignee="user",
                completed=True,
                execution="2026-01-02",
                assignee_email="user@test.com",
                assignee_discord_username="user",
                description="desc",
                periodicity="daily",
                category="cat",
            ),
            notification_client=notification_client,
            email_client=email_client,
        )
    )

    result = await use_case.execute()

    assert result.tid == "1"
    assert result.completed is True
    notification_client.update_notification.assert_awaited_once()
    notification_client.react.assert_awaited_once()
    notification_client.delete_reaction.assert_awaited_once()
    email_client.send_email.assert_awaited_once()
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.tasks.use_cases.delete_task.LogClient")
async def test_delete_task_use_case_should_delete_notification(mock_log_client_class):
    notification_client = MagicMock()
    notification_client.delete_notification = AsyncMock(return_value=None)

    use_case = DeleteTaskUseCase(
        DeleteTaskUseCaseInput(task_id="1", notification_client=notification_client)
    )

    result = await use_case.execute()

    assert result.task_id == "1"
    notification_client.delete_notification.assert_awaited_once()
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.tasks.use_cases.get_tasks.LogClient")
async def test_get_tasks_use_case_should_transform_notifications(mock_log_client_class):
    notification_client = MagicMock()
    notification_client.list_notifications = AsyncMock(
        return_value=[
            {
                "id": "1",
                "content": "## task\n__Estado__: Pendiente\n__Fecha limite__: 2026-01-01\n__Fecha creación__: 2025-12-01\n__Prioridad__: 1\n",
                "embeds": [],
                "reactions": [{"emoji": {"name": "📌"}}],
            }
        ]
    )

    use_case = GetTasksUseCase(
        GetTasksUseCaseInput(notification_client=notification_client, params={})
    )

    result = await use_case.execute()

    assert result.tasks[0]["task_id"] == "1"
    notification_client.list_notifications.assert_awaited_once()
    assert mock_log_client_class.called


@pytest.mark.asyncio
@patch("saviialib.services.tasks.use_cases.get_pending_tasks.LogClient")
@patch("saviialib.services.tasks.use_cases.get_pending_tasks.GetTasksUseCase")
async def test_get_pending_tasks_use_case_should_return_pending_tasks(
    mock_get_tasks_use_case_class,
    mock_log_client_class,
):
    notification_client = MagicMock()
    email_client = MagicMock()
    email_client.send_email = AsyncMock(return_value=None)
    dir_client = MagicMock()
    dir_client.path_exists = AsyncMock(return_value=True)
    dir_client.join_paths.side_effect = lambda *paths: "/".join(paths)
    dir_client.makedirs = AsyncMock(return_value=None)
    dir_client.touch = AsyncMock(return_value=None)

    mock_get_tasks_use_case_instance = mock_get_tasks_use_case_class.return_value
    mock_get_tasks_use_case_instance.execute = AsyncMock(
        return_value=MagicMock(
            tasks=[
                {
                    "title": "task",
                    "creation": "2025-12-01",
                    "deadline": "2026-01-01",
                    "execution": "",
                    "description": "desc",
                    "priority": "1",
                    "assignee": "user",
                    "assignee_email": "user@test.com",
                    "periodicity": "daily",
                }
            ]
        )
    )

    use_case = GetPendingTasksUseCase(
        GetPendingTasksUseCaseInput(
            notification_client=notification_client,
            email_client=email_client,
            dir_client=dir_client,
            local_backup_path="/tmp",
            download=False,
            notify=False,
        )
    )

    result = await use_case.execute()

    assert result.overdue or result.ontime
    mock_get_tasks_use_case_instance.execute.assert_awaited_once()
    assert mock_log_client_class.called
