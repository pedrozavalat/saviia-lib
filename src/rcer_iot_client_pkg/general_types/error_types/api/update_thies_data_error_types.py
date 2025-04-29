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
