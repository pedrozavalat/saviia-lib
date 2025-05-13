# read version from installed package
from importlib.metadata import version

__version__ = version("saviialib")

from .services.epii.api import EpiiAPI
from .general_types.api.epii_api_types import EpiiAPIConfig

__all__ = ["EpiiAPI", "EpiiAPIConfig"]
