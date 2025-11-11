"""
Shared utility functions for SHAED Order ELT
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from google.cloud import storage

from .config import GCS_BUCKET_NAME, GCS_BUCKET_PATH, OUTPUT_DIR


def clean_value(value: Any) -> str:
    """
    Clean and format value for CSV export - BigQuery compatible
    
    Args:
        value: Value to clean (can be any type)
        
    Returns:
        Cleaned string value
    """
    if value is None:
        return ''
    
    # Handle JSONB/JSON types (dict/list) - convert to JSON string
    if isinstance(value, (dict, list)):
        try:
            json_str = json.dumps(value, ensure_ascii=False)
            # Escape double quotes for CSV
            if '"' in json_str:
                json_str = json_str.replace('"', '""')
            return json_str
        except Exception:
            return str(value)
    
    # Handle datetime/timestamp objects
    if isinstance(value, datetime):
        return value.isoformat()
    
    # Handle boolean values
    if isinstance(value, bool):
        return str(value).lower()
    
    # Handle numeric types
    if isinstance(value, (int, float)):
        return str(value)
    
    # Handle string values - escape quotes and newlines
    if isinstance(value, str):
        # Replace newlines with spaces for CSV compatibility
        value = value.replace('\n', ' ').replace('\r', ' ')
        # Escape double quotes by doubling them
        if '"' in value:
            value = value.replace('"', '""')
        return value
    
    # Convert everything else to string
    return str(value)


def upload_to_gcs(file_path: Path, blob_name: Optional[str] = None) -> bool:
    """
    Upload a file to Google Cloud Storage
    
    Args:
        file_path: Local path to the file to upload
        blob_name: Optional custom blob name. If not provided, uses filename
        
    Returns:
        True if upload successful, False otherwise
    """
    if not file_path.exists():
        print(f"✗ Error: File not found: {file_path}")
        return False
    
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        
        if blob_name is None:
            blob_name = f"{GCS_BUCKET_PATH}/{file_path.name}"
        else:
            blob_name = f"{GCS_BUCKET_PATH}/{blob_name}"
        
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(str(file_path))
        
        print(f"✓ Successfully uploaded to gs://{GCS_BUCKET_NAME}/{blob_name}")
        return True
    except Exception as e:
        print(f"⚠ Warning: Failed to upload to GCS: {e}")
        return False


def get_timestamp_string() -> str:
    """
    Get current timestamp as string for filename
    
    Returns:
        Timestamp string in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def get_file_size_mb(file_path: Path) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    size_bytes = os.path.getsize(file_path)
    return size_bytes / (1024 * 1024)


def sanitize_column_name(col_name: str) -> str:
    """
    Sanitize column names for BigQuery compatibility.
    BigQuery field names must:
    - Start with a letter or underscore
    - Contain only letters, numbers, and underscores
    - Be case-sensitive
    - Not be reserved keywords
    
    Args:
        col_name: Column name to sanitize
        
    Returns:
        Sanitized column name
    """
    if not isinstance(col_name, str):
        col_name = str(col_name)
    
    # Remove leading/trailing whitespace
    col_name = col_name.strip()
    
    # Replace special characters with underscores
    # Replace spaces, slashes, hyphens, and other special chars
    col_name = re.sub(r'[^a-zA-Z0-9_]', '_', col_name)
    
    # Replace multiple underscores with single underscore
    col_name = re.sub(r'_+', '_', col_name)
    
    # Remove leading/trailing underscores
    col_name = col_name.strip('_')
    
    # If empty or starts with number, prefix with underscore
    if not col_name or col_name[0].isdigit():
        col_name = '_' + col_name
    
    # Ensure it's not empty (fallback)
    if not col_name:
        col_name = 'unnamed_column'
    
    return col_name

