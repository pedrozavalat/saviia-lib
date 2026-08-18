import unittest
from unittest.mock import Mock

from saviialib import SaviiaAPI, SaviiaAPIConfig


class TestSaviiaAPI(unittest.TestCase):
    def setUp(self):
        self.config = SaviiaAPIConfig(
            databricks_api_key="token",
            databricks_host_url="https://workspace.azuredatabricks.net",
            logger=Mock(),
            local_backup_path="/share/G",
        )

    def test_should_initialize_saviia_api_with_both_services(self):
        # Arrange
        api = SaviiaAPI(self.config)
        # Act & Assert
        self.assertIn("thies", api.list_available())
        self.assertIn("backup", api.list_available())
