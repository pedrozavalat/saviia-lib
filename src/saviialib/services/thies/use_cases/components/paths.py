import os
from typing import Literal


ThiesCategory = Literal["AVG", "EXT"]
THIES_CATEGORIES: tuple[ThiesCategory, ThiesCategory] = ("AVG", "EXT")


class ThiesPathComponent:
    """Build local, cloud, and FTP paths used by THIES workflows."""

    BASE_FOLDER_NAME = "thies"

    def __init__(
        self,
        local_backup_path: str,
        cloud_destination_path: str = "",
        ftp_folders: list[str] | None = None,
    ) -> None:
        self.local_backup_path = local_backup_path.rstrip("/")
        self.cloud_destination_path = cloud_destination_path.rstrip("/")
        self.ftp_folders = ftp_folders or []

    def get_backup_root_name(self) -> str:
        return os.path.basename(os.path.normpath(self.local_backup_path))

    def get_local_thies_path(self) -> str:
        return os.path.join(self.local_backup_path, self.BASE_FOLDER_NAME)

    def get_local_folder(self, category: ThiesCategory) -> str:
        return os.path.join(self.get_local_thies_path(), category)

    def get_cloud_thies_path(self) -> str:
        path = "/".join(
            part.strip("/")
            for part in (
                self.cloud_destination_path,
                self.get_backup_root_name(),
                self.BASE_FOLDER_NAME,
            )
            if part
        )
        return f"/{path}" if self.cloud_destination_path.startswith("/") else path

    def get_cloud_folder(self, category: ThiesCategory) -> str:
        return f"{self.get_cloud_thies_path().rstrip('/')}/{category}"

    @staticmethod
    def category_from_ftp_path(folder_path: str) -> ThiesCategory:
        return "AVG" if "AV" in folder_path.upper() else "EXT"

    def get_ftp_folder(self, category: ThiesCategory) -> str:
        for folder_path in self.ftp_folders:
            if self.category_from_ftp_path(folder_path) == category:
                return folder_path
        if self.ftp_folders:
            return self.ftp_folders[0]
        raise ValueError(f"FTP folder for category '{category}' is not configured")
