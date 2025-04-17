class ThiesUploadEmptyError(Exception):
    """Raised when no files are found to upload to the server."""

    def __str__(self):
        return "No files were found to upload."


class FetchCloudFileNamesError(Exception):
    """Raised when there is an error fetching file names from the RCER cloud."""

    def __str__(self):
        return "An error occurred while retrieving file names from the RCER cloud"


class FetchThiesFileContentError(Exception):
    """Raised when there is an error fetching the content of a Thies file."""

    def __str__(self):
        return "An error occurred while retrieving the content of a Thies file"
