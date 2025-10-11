import unittest
from unittest.mock import Mock

from saviialib import SaviiaAPI, SaviiaAPIConfig


class TestSaviiaAPI(unittest.TestCase):
    def setUp(self):
        self.config = SaviiaAPIConfig(
            ftp_host="ftp.example.com",
            ftp_port=21,
            ftp_user="user123",
            ftp_password="password123",
            sharepoint_client_id="client_id_123",
            sharepoint_client_secret="client_secret_123",
            sharepoint_tenant_id="tenant_id_123",
            sharepoint_tenant_name="tenant_name_123",
            sharepoint_site_name="site_name_123",
            logger=Mock(),
        )

    def test_should_initialize_saviia_api_with_both_services(self):
        # Arrange
        api = SaviiaAPI(self.config)
        # Act & Assert
        self.assertIn("thies", api.list_available())
        self.assertIn("backup", api.list_available())
