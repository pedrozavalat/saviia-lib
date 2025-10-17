import json


class ThiesConnectionError(Exception):
    """Raised when unable to connect to the THIES FTP Server"""

    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return "Unable to connect to THIES FTP Server. " + self.reason.__str__()


class ThiesFetchingError(Exception):
    """Raised when no files are found to upload to the server."""

    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return (
            "An error ocurred while retrieving files from THIES FTP Server. "
            + self.reason.__str__()
        )


class SharePointFetchingError(Exception):
    """Raised when there is an error fetching file names from the RCER cloud."""

    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        try:
            _, internal_metadata = self.reason.__str__().split(",", 1)
            internal_metadata_dict = json.loads(internal_metadata)
            return internal_metadata_dict["error_description"]

        except json.decoder.JSONDecodeError:
            return self.reason.__str__()


class SharePointDirectoryError(Exception):
    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return (
            "An error occurred while fetching the folders from Microsoft SharePoint. "
            + self.reason.__str__()
        )


class SharePointUploadError(Exception):
    """Raised when there is an error uploading files to the Microsoft SharePoint folder."""

    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return (
            "An error occurred while uploading files to the Microsoft SharePoint folder. "
            + self.reason.__str__()
        )


class BackupUploadError(Exception):
    """Raised when there is an error when occurs the migration from the local backup to
    sharepoint cloud."""

    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return (
            "An error occurred during the migration from the local backup to SharePoint cloud. "
            "Search the logs for more information. " + self.reason.__str__()
        )


class BackupSourcePathError(Exception):
    """Raised when the local backup source path is invalid."""

    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return "Invalid local backup source path. " + self.reason.__str__()


class BackupEmptyError(Exception):
    """Raised when the local backup folder is empty."""

    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return "The local backup folder is empty. "


class ShakesNoContentError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return "All the miniSEED files have been downloaded and are in the local directory."
