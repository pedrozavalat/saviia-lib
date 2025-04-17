# read version from installed package
from importlib.metadata import version

__version__ = version("rcer_iot_client_pkg")

from .services.epii.api import EpiiAPI

__all__ = ["EpiiAPI"]
