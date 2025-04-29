import asyncio
import os
from dotenv import load_dotenv
from rcer_iot_client_pkg import EpiiAPI, EpiiUpdateThiesConfig

load_dotenv()


async def main():
    api = EpiiAPI()
    config = EpiiUpdateThiesConfig(
        ftp_host="localhost",
        ftp_port=21,
        ftp_user="anonymous",
        ftp_password="12345678",
        sharepoint_client_id=os.getenv("CLIENT_ID"),
        sharepoint_client_secret=os.getenv("CLIENT_SECRET"),
        sharepoint_site_name=os.getenv("SITE_NAME"),
        sharepoint_tenant_id=os.getenv("TENANT_ID"),
        sharepoint_tenant_name=os.getenv("TENANT_NAME"),
    )
    print("[epii] Extracting files from thies FTP Server")
    synced_files = await api.update_thies_data(config)
    print(synced_files)
    print("[epii] Extracting files successfully")
    return synced_files


asyncio.run(main())
