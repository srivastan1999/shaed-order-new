#!/bin/bash
# Script to process data for 10.14.2025

echo "=========================================="
echo "Processing data for 10.14.2025"
echo "=========================================="
echo ""

# Option 1: Download and process in one command
echo "Option 1: Full pipeline (Download + Process)"
echo "--------------------------------------------"
echo "python run.py ford-pipeline --date 10.14.2025"
echo ""

# Option 2: Download first, then process
echo "Option 2: Download first, then process separately"
echo "--------------------------------------------"
echo "# Step 1: Download"
echo "python run.py download ford --date 10.14.2025"
echo ""
echo "# Step 2: Process"
echo "python run.py oem ford"
echo ""

# Option 3: Use backend API (date format: YYYY-MM-DD)
echo "Option 3: Use Backend API"
echo "--------------------------------------------"
echo "# Start backend first:"
echo "cd backend && uvicorn main:app --reload"
echo ""
echo "# Then in another terminal, process the date:"
echo "curl \"http://localhost:8000/api/ford-process-date?date=2025-10-14\""
echo ""

# Option 4: Process existing file if already downloaded
echo "Option 4: Process existing file (if already in data/input)"
echo "--------------------------------------------"
echo "python run.py oem ford --input-file \"data/input/Ford Dealer Report-10.14.2025.xlsx\""
echo ""

echo "=========================================="
echo "Date format notes:"
echo "- CLI commands use: MM.DD.YYYY (10.14.2025)"
echo "- API endpoints use: YYYY-MM-DD (2025-10-14)"
echo "=========================================="

