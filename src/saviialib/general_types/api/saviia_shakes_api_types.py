from dataclasses import dataclass
from logging import Logger


@dataclass
class SaviiaShakesConfig:
    """
    Configuration for Raspberry shakes activities as Miniseed extraction, photo record and video record.

    Attributes:
        sftp_user (str): Username for SFTP Client connection
        sftp_password (str): Password for SFTP Client connection
        sftp_port (str): SFTP Server Port. Default port is 22.
        ssh_key_path (str): Path to the SSH Private key for client-side authentication.
    """

    sftp_user: str
    sftp_password: str
    ssh_key_path: str
    logger: Logger
    sftp_port: int = 22
