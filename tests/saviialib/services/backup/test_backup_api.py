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
from saviialib.services.backup.api import SaviiaBackupAPI


@pytest.fixture
def backup_config() -> SaviiaBackupConfig:
    return SaviiaBackupConfig(
        sharepoint_client_id="client-id",
        sharepoint_client_secret="client-secret",
        sharepoint_tenant_id="tenant-id",
        sharepoint_tenant_name="tenant-name",
        sharepoint_site_name="site-name",
        logger=MagicMock(),
    )


@pytest.mark.asyncio
@patch("saviialib.services.backup.api.UploadBackupToSharepointController")
async def test_should_delegate_upload_backup_to_sharepoint(
    mock_controller_class, backup_config
):
    expected_response = MagicMock(message="ok", status=200, metadata={"data": "x"})
    mock_controller_instance = mock_controller_class.return_value
    mock_controller_instance.execute = AsyncMock(return_value=expected_response)

    api = SaviiaBackupAPI(backup_config)
    response = await api.upload_backup_to_sharepoint(
        local_backup_source_path="/tmp/local",
        sharepoint_destination_path="Shared%20Documents/backup",
    )

    assert response == expected_response.__dict__
    mock_controller_instance.execute.assert_awaited_once()
