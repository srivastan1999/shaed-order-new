# Common Commands

This document provides useful commands for working with the SHAED Order ELT project.

## Setup & Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install in development mode (optional)
pip install -e .
```

## Data Extraction Commands

### Extract Orders from PostgreSQL
```bash
# Extract orders and upload to GCS/BigQuery
python run.py orders

# Extract orders without uploading
python run.py orders --no-upload

# Extract to custom output directory
python run.py orders --output-dir /path/to/output
```

### Download OEM Files from GCS
```bash
# Download Ford files for a specific date
python run.py download ford --date 11.10.2025

# Download for multiple dates
python run.py download ford --date1 11.07.2025 --date2 11.10.2025

# Download using environment variables (DATE1, DATE2 from .env)
python run.py download ford --from-env

# Download to custom directory
python run.py download ford --date 11.10.2025 --output-dir /path/to/input
```

## Processing Commands

### Process OEM Files
```bash
# Process Ford files (searches data/input for Excel files)
python run.py oem ford

# Process specific file
python run.py oem ford --input-file "data/input/Ford Dealer Report-11.10.2025.xlsx"

# Process without uploading to GCS
python run.py oem ford --no-upload

# Process with custom directories
python run.py oem ford --input-dir /path/to/input --output-dir /path/to/output
```

### Full Pipeline (Download + Process)
```bash
# Download and process Ford files in one command
python run.py ford-pipeline --date 11.10.2025

# Using environment variables
python run.py ford-pipeline --from-env

# Multiple dates
python run.py ford-pipeline --date1 11.07.2025 --date2 11.10.2025

# Without uploading
python run.py ford-pipeline --date 11.10.2025 --no-upload
```

### Process All (Orders + All OEMs)
```bash
# Process orders and all OEM files
python run.py all

# Without uploading
python run.py all --no-upload
```

## Backend API Commands

### Start Backend Server
```bash
# Using uvicorn directly
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using the start script
./start_backend.sh

# Or from project root
python -m backend.main
```

### Test Backend Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Get field comparison
curl "http://localhost:8000/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10"

# Get field comparison stats
curl "http://localhost:8000/api/ford-field-comparison/stats?old_date=2025-11-07&new_date=2025-11-10"

# Process Ford date
curl "http://localhost:8000/api/ford-process-date?date=2025-11-10"

# Process with limit
curl "http://localhost:8000/api/ford-process-date?date=2025-11-10&limit=100"
```

## Development & Testing

### Run Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_utils.py

# Run with verbose output
python -m pytest tests/ -v
```

### Check Code Structure
```bash
# Verify imports work
python -c "from data_extraction import OEMDownloader, OrdersExtractor; print('✓ Data extraction imports OK')"
python -c "from processing.processors import OEM_PROCESSORS; print('✓ Processing imports OK')"
python -c "from shared.config import INPUT_DIR, OUTPUT_DIR; print('✓ Config imports OK')"

# Check Python syntax
python -m py_compile main.py
python -m py_compile run.py
```

### View Project Structure
```bash
# Tree view (if tree is installed)
tree -I '__pycache__|*.pyc|*.xlsx|*.csv' -L 3

# Or use find
find . -type f -name "*.py" | grep -v __pycache__ | sort
```

## Database & Cloud SQL Proxy

### Start Cloud SQL Proxy
```bash
# Using the start script
./start_proxy.sh

# Or manually
./cloud-sql-proxy --port=5555 PROJECT_ID:REGION:INSTANCE_NAME
```

### Test PostgreSQL Connection
```bash
# Using psql
psql -h localhost -p 5555 -U postgres -d postgres

# Test connection from Python
python -c "from data_extraction import OrdersExtractor; e = OrdersExtractor(); print('✓ Connection OK')"
```

## Environment Setup

### Create .env file
```bash
# Copy example if exists, or create new
cat > .env << EOF
# GCP Configuration
PROJECT_ID=your-project-id
BUCKET_NAME=your-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# GCS Upload Configuration
GCS_BUCKET_NAME=shaed-elt-csv
GCS_BUCKET_PATH=order_view_api

# Database Configuration
DB_HOST=localhost
DB_PORT=5555
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-password

# Download Dates (optional)
DATE1=11.07.2025
DATE2=11.10.2025
NAME_CONTAINS=Ford Dealer Report
EOF
```

## Cleanup Commands

### Clean Python Cache
```bash
# Remove all __pycache__ directories
find . -type d -name __pycache__ -exec rm -r {} +

# Remove .pyc files
find . -name "*.pyc" -delete
```

### Clean Data Files
```bash
# Remove input files (be careful!)
# rm -rf data/input/*.xlsx

# Remove output files (be careful!)
# rm -rf data/output/*.csv
```

## Quick Reference

### Most Common Workflows

**1. Daily Ford Processing:**
```bash
python run.py ford-pipeline --date $(date +%m.%d.%Y)
```

**2. Extract Orders:**
```bash
python run.py orders
```

**3. Process Existing Files:**
```bash
python run.py oem ford
```

**4. Start Backend:**
```bash
cd backend && uvicorn main:app --reload
```

**5. Full Pipeline (Orders + Ford):**
```bash
python run.py orders && python run.py ford-pipeline --from-env
```

## Troubleshooting

### Check Python Path
```bash
# Verify project root is in path
python -c "import sys; print('\n'.join(sys.path))"
```

### Verify Imports
```bash
# Test all main imports
python << EOF
from data_extraction import OEMDownloader, OrdersExtractor
from processing.processors import OEM_PROCESSORS
from processing.bigquery_loader import BigQueryLoader
from shared.config import INPUT_DIR, OUTPUT_DIR
print("✓ All imports successful!")
EOF
```

### Check File Permissions
```bash
# Make scripts executable
chmod +x run.py
chmod +x start_backend.sh
chmod +x start_proxy.sh
```

