"""
Rush Gaming Competitive Intelligence System

Automated monitoring and analysis of competitor activities in India's real-money gaming market.
"""

__version__ = "1.0.0"
__author__ = "Rush Gaming CI Team"
__email__ = "ci-team@rushgaming.com"

from .config import Config
from .utils.logger import setup_logger

# Setup default logger
logger = setup_logger()

__all__ = [
    "Config",
    "logger",
] 