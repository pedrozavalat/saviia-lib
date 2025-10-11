# SAVIIA Library 
*Sistema de Administración y Visualización de Información para la Investigación y Análisis*

[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pedrozavalat/saviia-lib?style=for-the-badge)](https://github.com/pedrozavalat/saviia-lib/releases)


## Installation
This library is designed for use with the SAVIIA Home Assistant Integration. It provides an API to retrieve files from a THIES Data Logger via an FTP server and upload them to a Microsoft SharePoint folder using the SharePoint REST API.

```bash
pip install saviialib
```

## Saviia API Client Usage

### Initialize the Saviia API Client
Import the necessary classes from the library.
```python
from saviialib import SaviiaAPI, SaviiaAPIConfig
```

To start using the library, you need to create an `SaviiaAPI` client instance with its configuration class `SaviiaAPIConfig`. Provide the required parameters such as FTP server details and SharePoint credentials:
```python
config = SaviiaAPIConfig(
    ftp_port=FTP_PORT,
    ftp_host=FTP_HOST,
    ftp_user=FTP_USER,
    ftp_password=FTP_PASSWORD,
    sharepoint_client_id=SHAREPOINT_CLIENT_ID,
    sharepoint_client_secret=SHAREPOINT_CLIENT_SECRET,
    sharepoint_tenant_id=SHAREPOINT_TENANT_ID,
    sharepoint_tenant_name=SHAREPOINT_TENANT_NAME,
    sharepoint_site_name=SHAREPOINT_SITE_NAME
)
```
```python
api_client = SaviiaAPI(config)
```
**Notes:** 
- Store sensitive data like `FTP_PASSWORD`, `FTP_USER`, and SharePoint credentials securely. Use environment variables or a secrets management tool to avoid hardcoding sensitive information in your codebase.

### Access THIES Data Logger Services
To interact with the THIES Data Logger services, you can access the `thies` attribute of the `SaviiaAPI` instance:
```python
thies_client = api_client.get('thies')
```
This instance provides methods to interact with the THIES Data Logger. Currently, it includes the main method for extracting files from the FTP server and uploading them to SharePoint.

#### THIES files extraction and synchronization
The library provides a method to extract and synchronize THIES Data Logger files with the Microsoft SharePoint client. This method downloads files from the FTP server and uploads them to the specified SharePoint folder:
```python 
import asyncio
async def main():
    # Before calling this method, you must have initialised the THIES service class ...
    response = await thies_client.update_thies_data()
    return response

asyncio.run(main())
```

### Access Backup Services
To interact with the Backup services, you can access the `backup` attribute of the `SaviiaAPI` instance:
```python
backup_client = api_client.get('backup')
```
This instance provides methods to interact with the Backup services. Currently, it includes the main method for creating backups of specified directories in a local folder from Home Assistant environment. Then each backup file is uploaded to a Microsoft SharePoint folder.

#### Create Backup
The library provides a method which creates a backup of a specified directory in a local folder from Home Assistant environment. Then each backup file is uploaded to a Microsoft SharePoint folder: 

```python
import asyncio
async def main():
    # Before calling this method, you must have initialised the Backup service class ...
    response = await backup_client.upload_backup_to_sharepoint(
        local_backup_path=LOCAL_BACKUP_PATH,
        sharepoint_folder_path=SHAREPOINT_FOLDER_PATH
    )
    return response
asyncio.run(main())
```
**Notes:**
- Ensure that the `local_backup_path` exists and contains the files you want to back up. It is a relative path from the Home Assistant configuration directory.
- The `sharepoint_folder_path` should be the path to the folder in SharePoint where you want to upload the backup files. For example, if your url is `https://yourtenant.sharepoint.com/sites/yoursite/Shared Documents/Backups`, the folder path would be `sites/yoursite/Shared Documents/Backups`.







## Contributing
If you're interested in contributing to this project, please follow the contributing guidelines. By contributing to this project, you agree to abide by its terms.
Contributions are welcome and appreciated!

## License

`saviialib` was created by Pedro Pablo Zavala Tejos. It is licensed under the terms of the MIT license.
