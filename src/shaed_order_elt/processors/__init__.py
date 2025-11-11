"""
Data processors for orders and OEM dealer reports

To add a new OEM:
1. Create a new file: oem_name.py
2. Create a class that inherits from BaseOEMProcessor
3. Add it to OEM_PROCESSORS below
"""

from .orders import OrdersProcessor
from .ford import FordProcessor

# Registry of available OEM processors
# Add new OEM processors here
OEM_PROCESSORS = {
    "ford": FordProcessor,
    # "toyota": ToyotaProcessor,  # Example: uncomment and import when ready
    # "gm": GMProcessor,           # Example: uncomment and import when ready
}

__all__ = [
    "OrdersProcessor",
    "FordProcessor",
    "OEM_PROCESSORS",
]

