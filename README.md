# ECHO Library 
> Edge Computing & Hardware Orchestration API library for Home Assistant. 



[![GitHub release (latest by date)](https://img.shields.io/github/v/release/pedrozavalat/saviia-lib?style=for-the-badge)](https://github.com/pedrozavalat/saviia-lib/releases)


## Table of Contents
- [Installation](#installation)
- [ECHO API Client Usage](#echo-api-client-usage)
     - [Initialize the ECHO API Client](#initialize-the-echo-api-client)
        - [Access THIES Data Logger Services](#access-thies-data-logger-services)
            - [THIES files extraction and synchronization](#thies-files-extraction-and-synchronization)
            - [Get THIES status](#get-thies-status)
            - [Post THIES precomputed actions](#post-thies-precomputed-actions)
            - [Detect Failures](#detect-failures)
        
        - [Access Backup Services](#access-backup-services)
            - [Create Backup](#create-backup)
            - [Export Files](#export-files)
        - [Access Netcamera Services](#access-netcamera-services)
            - [Get Camera Rates](#get-camera-rates)
        - [Access Task System Services](#access-task-system-services)
            - [Create Task](#create-task)
            - [Update Task](#update-task)
            - [Delete Task](#delete-task)
            - [Get Tasks](#get-tasks)
- [Related Projects](#related-projects)
- [Contributing](#contributing)
- [License](#license)

## Installation
This library is designed for use with the SAVIIA Home Assistant Integration. It provides an API to retrieve files from a THIES Data Logger via an FTP server and upload them to a Microsoft SharePoint folder using the SharePoint REST API.

```bash
pip install saviialib
```

## ECHO API Client Usage

### Initialize the ECHO API Client
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
thies_service = api_client.get('thies')
```
This instance provides methods to interact with the THIES Data Logger. Currently, it includes the main method for extracting files from the FTP server and uploading them to SharePoint.

#### THIES files extraction and synchronization
The library provides a method to extract and synchronize THIES Data Logger files with the Microsoft SharePoint client. This method downloads files from the FTP server and uploads them to the specified SharePoint folder:
```python 
import asyncio
async def main():
    # Before calling this method, you must have initialised the THIES service class ...
    response = await thies_service.update_thies_data()
    return response

asyncio.run(main())
```

##### Get THIES status
You can check whether THIES data needs syncing or backup by calling `get_thies_data` with FTP credentials and a SharePoint destination path:

```python
import asyncio

async def main():
    response = await thies_service.get_thies_data(
        ftp_port=21,
        ftp_host="ftp.example.com",
        ftp_user="anonymous",
        ftp_password="",
        sharepoint_destination_path="Shared%20Documents/General/Test_Raspberry/THIES/AVG",
    )
    return response

asyncio.run(main())
```

##### Post THIES precomputed actions
If you already computed whether to sync or backup externally, call `post_thies_data` to execute the actions:

```python
import asyncio

async def main():
    response = await thies_service.post_thies_data(
        ftp_port=21,
        ftp_host="ftp.example.com",
        ftp_user="anonymous",
        ftp_password="",
        need_to_sync=True,
        need_to_backup=False,
        sharepoint_destination_path="Shared%20Documents/General/Test_Raspberry/THIES/AVG",
        ftp_server_folders_path=["/ARCH_AV1", "/ARCH_EX1"],
        local_backup_source_path="saviia-local-backup",
    )
    return response

asyncio.run(main())
```

The `need_to_backup` allows you to trigger a backup of the THIES files in a local folder, while `need_to_sync` will trigger the synchronization of THIES files between the Local Backup and SharePoint. You can set either or both to `True` depending on your needs.

##### Detect Failures
Use `detect_failures` to scan a local backup folder for missing or corrupt THIES files over the last N days. 

```python
import asyncio

async def main():
    response = await thies_service.detect_failures(
        local_backup_source_path="saviia-local-backup",
        n_days=7
    )
    return response

asyncio.run(main())
```

### Access Backup Services
To interact with the Backup services, you can access the `backup` attribute of the `SaviiaAPI` instance:
```python
backup_service = api_client.get('backup')
```
This instance provides methods to interact with the Backup services. Currently, it includes the main method for creating backups of specified directories in a local folder from Home Assistant environment. Then each backup file is uploaded to a Microsoft SharePoint folder.

#### Create Backup
The library provides a method which creates a backup of a specified directory in a local folder from Home Assistant environment. Then each backup file is uploaded to a Microsoft SharePoint folder: 

```python
import asyncio
async def main():
    # Before calling this method, you must have initialised the Backup service class ...
    response = await backup_service.upload_backup_to_sharepoint(
        local_backup_path=LOCAL_BACKUP_PATH,
        sharepoint_folder_path=SHAREPOINT_FOLDER_PATH
    )
    return response
asyncio.run(main())
```
**Notes:**
- Ensure that the `local_backup_path` exists and contains the files you want to back up. It is a relative path from the Home Assistant configuration directory.
- The `sharepoint_folder_path` should be the path to the folder in SharePoint where you want to upload the backup files. For example, if your url is `https://yourtenant.sharepoint.com/sites/yoursite/Shared Documents/Backups`, the folder path would be `sites/yoursite/Shared Documents/Backups`.

#### Export Files
Use `export_files` to synchronize a local folder (under the configured backup root) with a specific SharePoint destination. This method validates the local folder, compares local files with SharePoint (existence and file size) and uploads only the missing or size-different files.

Example usage:
```python
import asyncio

async def main():
    # backup_service was obtained from SaviiaAPI as shown above
    # `local_folder_path` is a relative path under your configured local backup root,
    # for example: "thies/AVG"
    response = await backup_service.export_files(
        local_folder_path="thies/AVG",
        sharepoint_destination_path="Shared%20Documents/General/Test_Raspberry/saviia-local-backup/thies/AVG"
    )
    return response

asyncio.run(main())
```

Notes:
- `local_folder_path`: relative folder under your configured `local_backup_path` where files are read from.
- `sharepoint_destination_path`: the exact destination folder in SharePoint where files will be created/uploaded. The controller will add the server-relative prefix (e.g. `/sites/{site_name}`) when required.
- The controller is responsible for instantiating the external clients (SharePoint, file reader, directory client); the use case only contains orchestration and business logic.
- If SharePoint reports a file size of zero for a remote item, the code treats that as "unknown" and will not force a resync based solely on a zero-length remote size. Only files that are missing in SharePoint or that have differing non-zero sizes will be uploaded.

### Access Netcamera Services
The Netcamera service provides camera capture rate configuration based on meteorological data such as precipitation and precipitation probability.

This service uses the Weather Client library, currently implemented with OpenMeteo, and is designed to be extensible for future weather providers.

```python 
netcamera_service = api_client.get("netcamera")
```
#### Get Camera Rates
Returns photo and video capture rates for a camera installed at a given geographic location.
```python 
import asyncio

async def main():
    lat, lon = 10.511223, 20.123123
    camera_rates = await netcamera_service.get_camera_rates(latitude=lat, longitude=lon)
    return camera_rates
asyncio.run(main())
```
Example output:
```python 
{
    "status": "A",          # B or C
    "photo_rate": number,   # in minutes
    "video_rate": number    # in minutes
}
```
#### Description:
* The capture rate is calculated using meteorological metrics:
    * Precipitation
    * Precipitation probability
* The resulting configuration determines the camera capture frequency.

#### Status variable
The status variable is classified based on weather conditions (currently, precipitation and precipitation probability) at the camera's location:

| Status | 1 photo capture per | 1 video capture per |
| --- | --- | --- |
| A | 12 h | 12 h |
| B | 30 min | 3 h |
| C | 5 min | 1 h |


### Access Task System Services
To interact with the Task System services, you can access the `tasks` attribute of the `SaviiaAPI` instance:
```python
tasks_service = api_client.get('tasks')
```
This instance provides methods to manage tasks in specified channels. Note that this service requires an existing bot to be set up in the Discord server to function properly.

For using the Tasks Services, you need to provide the additional parameters `bot_token` and `task_channel_id` in the `SaviiaAPIConfig` configuration class:

```python
config = SaviiaAPIConfig(
    ... 
    task_channel_id=TASK_CHANNEL_ID,
    bot_token=BOT_TOKEN
)
```
The `task_channel_id` is the ID of the Discord channel where tasks will be created, updated, and deleted. The `bot_token` is the token of the Discord bot that has permissions to manage messages in that channel.


#### Create Task
Create a new task in a Discord channel with the following properties:
```python
import asyncio

async def main():
    response = await tasks_service.create_task(
        task={
            "name": "Task Title",
            "description": "Task Description",
            "due_date": "2024-12-31T23:59:59Z",
            "priority": 1,
            "assignee": "user_name",
            "category": "work",
        },
         images=[
            {
                "name": "image.png",
                "type": "image/png",
                "data": "base64_encoded_data"
            }
        ],
        config=config
    )
    return response

asyncio.run(main())
```
**Notes:**
- `name`, `description`, `due_date`, `priority`, `assignee`, and `category` are required.
- `images` is optional and accepts up to 10 images.
- `due_date` must be in ISO 8601 format (datetime).
- `priority` must be an integer between 1 and 4.

#### Update Task
Update an existing task or mark it as completed. The task will be reacted with ✅ if completed or 📌 if pending:
```python
import asyncio

async def main():
    response = await tasks_service.update_task(
        task={
            "id": "task_id",
            "name": "Updated Title",
            "description": "Updated Description",
            "due_date": "2024-12-31T23:59:59Z",
            "priority": 2,
            "assignee": "updated_user_name",
            "category": "work"
        }, # Must contain all the attributes of the task
        completed=True,
        config=config
    )
    return response

asyncio.run(main())
```


#### Delete Task
Delete an existing task from a Discord channel by providing its ID:
```python
import asyncio

async def main():
    response = await tasks_service.delete_task(
        task_id="task_id",
        config=config
    )
    return response

asyncio.run(main())
```

#### Get Tasks
Retrieve tasks from a Discord channel with optional filtering and sorting:
```python
import asyncio

async def main():
    response = await tasks_service.get_tasks(
        params={
            "sort": "desc",
            "completed": False,
            "fields": ["title", "due_date", "priority"],
            "after": 1000000,
            "before": 2000000
        },
        config=config
    )
    return response

asyncio.run(main())
```
**Notes:**
- `sort`: Order results by `asc` or `desc`.
- `completed`: Filter tasks by completion status.
- `fields`: Specify which fields to include in the response. Must include `title` and `due_date`.
- `after` and `before`: Filter tasks by timestamp ranges.

#### Get Pending Tasks
To retrieve pending (uncompleted) tasks and optionally download attachments or trigger notifications, call `get_pending_tasks`:

```python
import asyncio

async def main():
    # download: if True, attachments for pending tasks will be downloaded
    # notify: if True, the configured bot will send notifications for pending tasks
    response = await tasks_service.get_pending_tasks(download=False, notify=False)
    return response

asyncio.run(main())
```
The notifications are sent as messages in the configured Discord channel, mentioning the assignee of each pending task with its title and due date.



## Contributing
If you're interested in contributing to this project, please follow the contributing guidelines. By contributing to this project, you agree to abide by its terms.
Contributions are welcome and appreciated!

## Related Projects
* [ECHO](https://github.com/raxlab/echo): A Home Assistant custom integration for Edge Computing and Hardware Orchestration that uses this library.

## License

`saviialib` was created by Pedro Pablo Zavala Tejos. It is licensed under the terms of the MIT license.
