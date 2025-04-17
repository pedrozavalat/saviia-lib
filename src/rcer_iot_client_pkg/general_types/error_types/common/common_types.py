class EmptyDataError(Exception):
    def __str__(self):
        return "The data provided is empty."


class HttpClientError(Exception):
    def __str__(self):
        return "Http Client initialization fails."


class FtpClientError(Exception):
    def __str__(self):
        return "Ftp Client initialization fails."
