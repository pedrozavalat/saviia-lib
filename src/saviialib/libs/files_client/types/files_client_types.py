from dataclasses import dataclass
from typing import Literal, Union, List, Dict


@dataclass
class FilesClientInitArgs:
    client_name: str = "aiofiles_client"


@dataclass
class ReadArgs:
    """
    Represents the arguments required to read a file.

    Attributes:
        file_path (str): The path to the file to be read.
        mode (Literal['r', 'rb']): The mode in which the file should be opened.
            - 'r': Open for reading (text mode).
            - 'rb': Open for reading (binary mode).
    """

    file_path: str
    mode: Literal["r", "rb", "json"]
    encoding: str = "utf-8"


@dataclass
class WriteArgs:
    file_name: str
    file_content: Union[str, bytes, List[Dict]]
    mode: Literal["w", "wb", "a", "json"]
    destination_path: str = ""
