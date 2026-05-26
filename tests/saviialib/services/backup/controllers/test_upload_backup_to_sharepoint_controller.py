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

from saviialib.general_types.api.saviia_backup_api_types import SaviiaBackupConfig
from saviialib.services.backup.controllers.types.upload_backup_to_sharepoint_types import (
    UploadBackupToSharepointControllerInput,
)
from saviialib.services.backup.controllers.upload_backup_to_sharepoint import (
    UploadBackupToSharepointController,
)


@pytest.fixture
def backup_config() -> SaviiaBackupConfig:
    return SaviiaBackupConfig(
        sharepoint_client_id="client-id",
        sharepoint_client_secret="client-secret",
        sharepoint_tenant_id="tenant-id",
        sharepoint_tenant_name="tenant-name",
        sharepoint_site_name="site-name",
        logger=MagicMock(),
        local_backup_path="/tmp/backup",
    )


@pytest.mark.asyncio
@patch(
    "saviialib.services.backup.controllers.upload_backup_to_sharepoint.UploadBackupToSharepointUsecase"
)
async def test_backup_controller_should_wrap_use_case_response(
    mock_use_case_class, backup_config
):
    mock_use_case_instance = mock_use_case_class.return_value
    mock_use_case_instance.execute = AsyncMock(
        return_value={"new_files": 1, "uploaded": True}
    )

    controller = UploadBackupToSharepointController(
        UploadBackupToSharepointControllerInput(
            backup_config,
            "/tmp/local",
            "Shared%20Documents/backup",
        )
    )

    result = await controller.execute()

    assert result.message == "Local backup was migrated successfully"
    assert result.status == 200
    assert result.metadata == {"data": {"new_files": 1, "uploaded": True}}
    mock_use_case_instance.execute.assert_awaited_once()
