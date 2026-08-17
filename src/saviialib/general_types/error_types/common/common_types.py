class EmptyDataError(Exception):
    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return "The data provided is empty. " + self.reason.__str__()


class CloudClientError(Exception):
    def __str__(self):
        return "Cloud Provider Client initialization fails."


class FtpClientError(Exception):
    def __str__(self):
        return "Ftp Client initialization fails."


class SftpClientError(Exception):
    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return "SFTP Client initialization fails." + self.reason.__str__()
