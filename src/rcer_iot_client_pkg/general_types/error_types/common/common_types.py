class EmptyDataError(Exception):
    def __str__(self):
        return "The data provided is empty."


class SharepointClientError(Exception):
    def __str__(self):
        return "SharePoint API REST Client initialization fails."


class FtpClientError(Exception):
    def __str__(self):
        return "Ftp Client initialization fails."
