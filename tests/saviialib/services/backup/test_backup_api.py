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
        client_name="databricks",
        databricks_api_key="token",
        databricks_host_url="https://workspace.azuredatabricks.net",
        logger=MagicMock(),
        local_backup_path="/tmp/backup",
    )


@pytest.mark.asyncio
@patch("saviialib.services.backup.api.ExportFilesController")
async def test_should_delegate_export_files(mock_controller_class, backup_config):
    expected_response = MagicMock(message="ok", status=200, metadata={"data": "x"})
    mock_controller_instance = mock_controller_class.return_value
    mock_controller_instance.execute = AsyncMock(return_value=expected_response)

    api = SaviiaBackupAPI(backup_config)
    response = await api.export_files(
        local_folder_path="thies-daily-files",
        cloud_provider_destination_path="/Volumes/catalog/schema/volume",
    )

    assert response == expected_response.__dict__
    mock_controller_instance.execute.assert_awaited_once()
