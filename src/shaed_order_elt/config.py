"""
Configuration module for SHAED Order ELT
"""

import os
from pathlib import Path
from typing import Optional

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Try to load .env file if python-dotenv is available
try:
    from dotenv import load_dotenv
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        load_dotenv(env_file)
except ImportError:
    pass

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
INPUT_DIR = DATA_DIR / "input"
OUTPUT_DIR = DATA_DIR / "output"

# Configuration directories
CONFIG_DIR = PROJECT_ROOT / "config"

# GCS Configuration (for uploading cleaned files)
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "shaed-elt-csv")
GCS_BUCKET_PATH = os.getenv("GCS_BUCKET_PATH", "order_view_api")

# GCS Download Configuration (for downloading source files)
DOWNLOAD_PROJECT_ID = os.getenv("PROJECT_ID")
DOWNLOAD_BUCKET_NAME = os.getenv("BUCKET_NAME", "pni-sheets")
DOWNLOAD_DATE1 = os.getenv("DATE1")  # Optional: MM.DD.YYYY format
DOWNLOAD_DATE2 = os.getenv("DATE2")  # Optional: MM.DD.YYYY format
ORDERS_TABLE_DATE = os.getenv("ORDERS_TABLE_DATE")  # Date for creating orders table: MM.DD.YYYY format (e.g., "11.07.2025")
NAME_CONTAINS = os.getenv("NAME_CONTAINS", "Ford Dealer Report")

# PostgreSQL Configuration
# Note: DB_PASSWORD should be set via environment variable or .env file for security
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5555"))  # Cloud SQL Proxy port
DB_NAME = os.getenv("DB_NAME", "postgres")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# SQL Query for Orders
ORDERS_QUERY = '''
SELECT * FROM v_orders_api 
WHERE "orderType" = 'order';
'''

# Ford Excel file pattern - supports both .xls and .xlsx
FORD_EXCEL_PATTERN = "Ford Dealer Report*.xls*"

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

