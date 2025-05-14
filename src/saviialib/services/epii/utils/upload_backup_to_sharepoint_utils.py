import re
from logging import Logger
from typing import List, Dict, Optional
from saviialib.general_types.error_types.api.epii_api_error_types import (
    BackupSourcePathError,
)
from saviialib.libs.directory_client import DirectoryClient, DirectoryClientArgs

dir_client = DirectoryClient(DirectoryClientArgs(client_name="os_client"))


def extract_error_information(error: str) -> Optional[Dict[str, str]]:
    match = re.search(r"(\d+), message='([^']*)', url=\"([^\"]*)\"", error)
    if match:
        return {
            "status_code": match.group(1),
            "message": match.group(2),
            "url": match.group(3),
        }
    return None


def explain_status_code(status_code: int) -> str:
    explanations = {
        404: "Probably an error with file or folder source path.",
        403: "Permission denied when accessing the source path.",
        500: "Internal server error occurred during upload.",
    }
    return explanations.get(status_code, "Unknown error occurred.")


def extract_error_message(logger: Logger, results: List[Dict], success: float) -> str:
    logger.info(
        "[local_backup_lib] Not all files uploaded ⚠️\n"
        f"[local_backup_lib] Files failed to upload: {(1 - success):.2%}"
    )

    failed_files = [item for item in results if not item.get("uploaded")]

    error_data = []
    for item in failed_files:
        error_info = extract_error_information(item.get("error_message", ""))
        if error_info:
            error_data.append(
                {
                    "file_name": item["file_name"],
                    "status_code": error_info["status_code"],
                    "message": error_info["message"],
                    "url": error_info["url"],
                }
            )

    # Group errors by code.
    grouped_errors: Dict[str, List[Dict]] = {}
    for error in error_data:
        code = error["status_code"]
        grouped_errors.setdefault(code, []).append(error)

    # Summary
    for code, items in grouped_errors.items():
        logger.info(
            f"[local_backup_lib] Status code {code} - {explain_status_code(int(code))}"
        )
        for item in items:
            logger.info(
                f"[local_backup_lib] File {item['file_name']}, url: {item['url']}, message: {item['message']}"
            )

    failed_file_names = [item["file_name"] for item in failed_files]
    return f"Failed files: {', '.join(failed_file_names)}."


def parse_execute_response(results: List[Dict]) -> Dict[str, List[str]]:
    try:
        return {
            "new_files": len(
                [item["file_name"] for item in results if item.get("uploaded")]
            ),
        }
    except (IsADirectoryError, AttributeError, ConnectionError) as error:
        raise BackupSourcePathError(reason=error)


def show_upload_result(uploaded: bool, file_name: str) -> str:
    status = "✅" if uploaded else "❌"
    message = "was uploaded successfully" if uploaded else "failed to upload"
    result = f"[local_backup_lib] File {file_name} {message} {status}"
    return result


def calculate_percentage_uploaded(results: List[Dict], total_files: int) -> float:
    uploaded_count = sum(
        1 for result in results if isinstance(result, dict) and result.get("uploaded")
    )
    return (uploaded_count / total_files) * 100 if total_files > 0 else 0


async def count_files_in_directory(path: str, folder_name: str) -> int:
    return len(await dir_client.listdir(dir_client.join_paths(path, folder_name)))
