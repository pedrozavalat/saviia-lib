from logging import Logger

from saviialib.libs.log_client import (
    DebugArgs,
    ErrorArgs,
    LogClient,
    LogClientArgs,
    LogStatus,
    WarningArgs,
)


class ThiesComponent:
    """Common logging behavior for reusable THIES components."""

    def __init__(self, class_name: str, logger: Logger | None = None) -> None:
        self.log_client = LogClient(
            LogClientArgs(
                client_name="logging",
                service_name="thies",
                class_name=class_name,
                logger=logger,
            )
        )

    def _debug(self, method_name: str, status: LogStatus, message: str = "") -> None:
        self.log_client.method_name = method_name
        metadata = {"msg": message} if message else {}
        self.log_client.debug(DebugArgs(status=status, metadata=metadata))

    def _warning(self, method_name: str, message: str) -> None:
        self.log_client.method_name = method_name
        self.log_client.warning(
            WarningArgs(status=LogStatus.FAILED, metadata={"msg": message})
        )

    def _error(self, method_name: str, message: str, error: Exception) -> None:
        self.log_client.method_name = method_name
        self.log_client.error(
            ErrorArgs(
                status=LogStatus.ERROR,
                metadata={"msg": f"{message}; error={type(error).__name__}: {error}"},
            )
        )
