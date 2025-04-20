# read version from installed package
from importlib.metadata import version

__version__ = version("rcer_iot_client_pkg")

from .services.epii.api import EpiiAPI
from .general_types.api.update_thies_data_types import EpiiAPIConfig

__all__ = ["EpiiAPI", "EpiiAPIConfig"]
