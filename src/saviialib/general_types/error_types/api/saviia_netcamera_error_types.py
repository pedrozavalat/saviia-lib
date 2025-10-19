class NetcameraConnectionError(Exception):
    def __init__(self, *args, reason):
        super().__init__(*args, reason)
        self.reason = reason

    def __str__(self):
        return "Netcamera Connection failed. " + self.reason.__str__()
