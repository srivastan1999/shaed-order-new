"""
Processing/Transformation Layer
Handles data processing, transformation, and loading to BigQuery
"""

from .processors import OEM_PROCESSORS, FordProcessor
from .bigquery_loader import BigQueryLoader

__all__ = [
    "OEM_PROCESSORS",
    "FordProcessor",
    "BigQueryLoader",
]

