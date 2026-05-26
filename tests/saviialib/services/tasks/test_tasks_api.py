import sys
import types
from unittest.mock import AsyncMock, MagicMock

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
from saviialib.services.tasks.api import SaviiaTasksAPI


@pytest.fixture
def tasks_config() -> SaviiaTasksConfig:
    return SaviiaTasksConfig(
        bot_token="token",
        task_channel_id="chan",
        email_address="mail@test.com",
        email_password="pwd",
        local_backup_path="/tmp",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "controller_path", "kwargs", "expected_input"),
    [
        (
            "create_task",
            "CreateTaskController",
            {"task": {"title": "t"}, "images": []},
            {"task": {"title": "t"}, "images": []},
        ),
        (
            "update_task",
            "UpdateTaskController",
            {"task": {"tid": "1"}, "completed": True},
            {"task": {"tid": "1"}, "completed": True},
        ),
        ("delete_task", "DeleteTaskController", {"task_id": "1"}, {"task_id": "1"}),
        (
            "get_tasks",
            "GetTasksController",
            {"params": {"completed": False}},
            {"params": {"completed": False}},
        ),
        (
            "get_pending_tasks",
            "GetPendingTasksController",
            {"download": True, "notify": True},
            {"download": True, "notify": True},
        ),
    ],
)
async def test_should_delegate_tasks_api_calls(
    monkeypatch, tasks_config, method_name, controller_path, kwargs, expected_input
):
    module = __import__("saviialib.services.tasks.api", fromlist=[controller_path])
    fake_output = MagicMock(message="ok", status=200, metadata={"id": "1"})
    fake_controller = MagicMock(execute=AsyncMock(return_value=fake_output))
    fake_input_ctor = MagicMock(
        side_effect=lambda *args, **kw: {"args": args, "kwargs": kw}
    )

    monkeypatch.setattr(
        module, controller_path, MagicMock(return_value=fake_controller)
    )
    monkeypatch.setattr(module, f"{controller_path}Input", fake_input_ctor)

    api = SaviiaTasksAPI(tasks_config)
    result = await getattr(api, method_name)(**kwargs)

    assert result == fake_output.__dict__
    fake_controller.execute.assert_awaited_once()
