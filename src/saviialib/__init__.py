# read version from installed package
from importlib.metadata import version

__version__ = version("saviialib")

from .services.epii.api import EpiiAPI
from .general_types.api.update_thies_data_types import EpiiUpdateThiesConfig

__all__ = ["EpiiAPI", "EpiiUpdateThiesConfig"]
