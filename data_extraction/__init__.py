"""
Data Extraction Layer
Handles downloading and extracting data from various sources (GCS, PostgreSQL, etc.)
"""

from .downloader import GCSDownloader, OEMDownloader
from .orders_extractor import OrdersExtractor

__all__ = [
    "GCSDownloader",
    "OEMDownloader",
    "OrdersExtractor",
]

