from typing import List, Dict
from saviialib.general_types.error_types.api.saviia_api_error_types import (
    BackupSourcePathError,
)
from saviialib.libs.zero_dependency.utils.booleans_utils import boolean_to_emoji
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs
from saviialib.libs.sharepoint_client import (
    SpListFilesArgs,
)
from saviialib.libs.files_client import (
    WriteArgs,
)

dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))


async def get_pending_files_for_folder(
    sharepoint_client,
    dir_client,
    sharepoint_path: str,
    local_files: set[str],
    failed_files: set[str],
) -> tuple[set[str], str]:
    folders = extract_folders_from_files(local_files)
    sharepoint_files = set()

    async with sharepoint_client:
        for folder in folders:
            files = await sharepoint_client.list_files(
                SpListFilesArgs(f"{sharepoint_path}/{folder}")
            )
            sharepoint_files.update(x["Name"] for x in files["value"])  # type: ignore

    local_basenames = {dir_client.get_basename(f) for f in local_files}
    pending_files = local_basenames.difference(sharepoint_files).union(failed_files)
    summary_msg = (
        f"SharePoint Files: {len(sharepoint_files)}. "
        f"Local Files: {len(local_files)}. "
        f"Failed files: {len(failed_files)}. "
        f"Pending Files: {len(pending_files)}. "
    )
    return pending_files, summary_msg


def parse_execute_response(results: List[Dict]) -> Dict[str, List[str]]:
    try:
        return {
            "new_files": len(
                [item["file_name"] for item in results if item.get("uploaded")]  # type: ignore
            ),
        }
    except (IsADirectoryError, AttributeError, ConnectionError) as error:
        raise BackupSourcePathError(reason=error)


def show_upload_result(uploaded: bool, file_name: str, error_message: str = "") -> str:
    status = boolean_to_emoji(uploaded)
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


async def count_files_in_directory(base_path: str, folder_name: str) -> int:
    full_path = dir_client.join_paths(base_path, folder_name)
    count = 0
    tree = await dir_client.walk(full_path)
    for root, _, files in tree:
        count += len(files)
    return count


def extract_folders_from_files(files: set[str]) -> set[str]:
    folders = set()
    for f in files:
        parts = f.split("/")
        if len(parts) > 1:
            for i in range(1, len(parts)):
                folders.add("/".join(parts[:i]))
    return folders


async def save_file(files_client, file_name, file_content, mode):
    await files_client.write(
        WriteArgs(
            file_name=file_name,
            file_content=file_content,  # type: ignore
            mode=mode,
        )
    )
