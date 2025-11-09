import re
from logging import Logger
from typing import List, Dict, Optional
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs

dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))


def parse_execute_response(results: List[Dict]) -> Dict[str, List[str]]:
    try:
        return {
            "new_files": len(
                [item["file_name"] for item in results if item.get("uploaded")] # type: ignore
            ),
        }
    except (IsADirectoryError, AttributeError, ConnectionError) as error:
        raise BackupSourcePathError(reason=error)


def show_upload_result(uploaded: bool, file_name: str, error_message: str = "") -> str:
    status = "✅" if uploaded else "❌"
    message = (
        "was uploaded successfully"
        if uploaded
        else f"failed to upload. Error: {error_message}"
    )
    result = f"File {file_name} {message} {status}"
    return result


def calculate_percentage_uploaded(results: List[Dict], total_files: int) -> float:
    uploaded_count = sum(
        1 for result in results if isinstance(result, dict) and result.get("uploaded")
    )
    return (uploaded_count / total_files) * 100 if total_files > 0 else 0


async def count_files_in_directory(path: str, folder_name: str) -> int:
    return len(await dir_client.listdir(dir_client.join_paths(path, folder_name)))
