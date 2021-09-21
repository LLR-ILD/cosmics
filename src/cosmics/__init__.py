"""Code useful for cosmic studies with the CALICE SiW-ECAL proposed for ILD."""
import logging

from .version import __version__

_version_info = f"{__name__} version {__version__} at {__file__[:-len('/__init__.py')]}"
logger = logging.getLogger(__name__)
logger.debug(_version_info)

__all__ = [
    "__version__",
]
