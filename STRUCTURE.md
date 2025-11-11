# Project Structure

This document describes the reorganized file structure of the SHAED Order ELT project.

## Directory Structure

```
shaed_order_elt/
├── data_extraction/          # Data Extraction Layer
│   ├── __init__.py
│   ├── downloader.py         # GCS downloader for OEM files
│   └── orders_extractor.py   # PostgreSQL orders extraction
│
├── processing/               # Processing/Transformation Layer
│   ├── __init__.py
│   ├── utils.py             # Shared utility functions
│   ├── bigquery_loader.py    # BigQuery data loading
│   └── processors/           # OEM-specific processors
│       ├── __init__.py
│       ├── base_oem.py      # Base class for OEM processors
│       └── ford.py          # Ford-specific processor
│
├── backend/                  # Backend API Layer
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── models/              # Response models
│   └── services/            # Backend services
│       ├── bigquery_service.py
│       └── processing_service.py
│
├── shared/                   # Shared Configuration
│   ├── __init__.py
│   └── config.py            # Configuration settings
│
├── data/                     # Data Storage
│   ├── input/               # Input files (Excel files from GCS)
│   └── output/              # Output files (processed CSV files)
│
├── tests/                    # Test files
├── main.py                   # CLI entry point
├── run.py                    # Wrapper script for CLI
└── setup.py                 # Package setup
```

## Layer Descriptions

### 1. Data Extraction Layer (`data_extraction/`)
**Purpose**: Extract and download data from various sources

- **`downloader.py`**: Downloads OEM Excel files from Google Cloud Storage
  - `GCSDownloader`: Generic GCS file downloader
  - `OEMDownloader`: OEM-specific file downloader

- **`orders_extractor.py`**: Extracts orders data from PostgreSQL database
  - `OrdersExtractor`: Exports orders to CSV format

### 2. Processing/Transformation Layer (`processing/`)
**Purpose**: Process, transform, and load data to BigQuery

- **`processors/`**: OEM-specific data processors
  - `base_oem.py`: Base class for all OEM processors
  - `ford.py`: Ford-specific data transformations

- **`bigquery_loader.py`**: Loads processed CSV files to BigQuery tables
  - `BigQueryLoader`: Handles BigQuery table creation and data loading

- **`utils.py`**: Shared utility functions
  - Data cleaning, GCS upload, column name sanitization, etc.

### 3. Backend Layer (`backend/`)
**Purpose**: FastAPI backend for querying and processing data

- **`main.py`**: FastAPI application with API endpoints
- **`services/`**: Business logic services
  - `bigquery_service.py`: BigQuery query execution
  - `processing_service.py`: Data processing pipeline orchestration
- **`models/`**: Pydantic response models

### 4. Shared Configuration (`shared/`)
**Purpose**: Centralized configuration

- **`config.py`**: All configuration settings (GCS, database, paths, etc.)

## Usage

### CLI Commands
```bash
# Extract orders from PostgreSQL
python run.py orders

# Download OEM files from GCS
python run.py download ford --date 11.10.2025

# Process OEM files
python run.py oem ford

# Full pipeline (download + process)
python run.py ford-pipeline --date 11.10.2025
```

### Backend API
```bash
# Start backend server
cd backend
python -m backend.main
# or
uvicorn backend.main:app --reload
```

## Import Patterns

### From Data Extraction Layer
```python
from data_extraction import OEMDownloader, OrdersExtractor
```

### From Processing Layer
```python
from processing.processors import OEM_PROCESSORS, FordProcessor
from processing.bigquery_loader import BigQueryLoader
from processing.utils import upload_to_gcs, sanitize_column_name
```

### From Shared Config
```python
from shared.config import INPUT_DIR, OUTPUT_DIR, GCS_BUCKET_NAME
```

## Migration Notes

- The old `src/shaed_order_elt/` structure has been replaced
- `OrdersProcessor` is now `OrdersExtractor` (alias maintained for compatibility)
- All imports have been updated to use the new structure
- Configuration is now centralized in `shared/config.py`

