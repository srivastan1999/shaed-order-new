# SHAED Order ELT

Clean, transform, and upload order data and OEM dealer reports to Google Cloud Storage.

## Quick Start

### 1. Configuration (Already Done!)

**Single command - Downloads TODAY's data automatically:**
```bash
# Ford only (no database needed)
python run.py ford-pipeline --from-env

# With database - orders + Ford
# Terminal 1: ./start_proxy.sh
# Terminal 2:
python run.py orders
python run.py ford-pipeline --from-env
```

### What Happens

1. **Download**: Gets TODAY's Ford file from GCS
2. **Process**: Cleans and converts to CSV
3. **Output**: `Ford_Dealer_Report_clean_20251105.csv` (date from source file)
4. **Upload**: Uploads to GCS bucket

## Individual Commands

```bash
# Download Ford files
python run.py download ford --from-env

# Export orders from database
python run.py orders

# Process Ford files
python run.py oem ford

# Everything at once
python run.py all
```

## Configuration

Edit `.env` file to change:
- `DATE1` and `DATE2` - Dates to download
- `DB_PASSWORD` - Database password
- `GOOGLE_APPLICATION_CREDENTIALS` - GCS credentials path

## Available Scripts

| Script | What It Does |
|--------|--------------|
| `start_proxy.sh` | Start Cloud SQL Proxy |
| `complete_workflow.sh` | Download + Orders + Ford |
| `download_and_process.sh` | Download + Ford only (no DB) |
| `test_database.sh` | Test database connection |
| `test_ford_workflow.sh` | Test Ford workflow |
| `test_setup.sh` | Test overall setup |

## Output

- **Input**: `data/input/` (downloaded Excel files)
- **Output**: `data/output/` (cleaned CSV files)
- **GCS**: `gs://shaed-elt-csv/order_view_api/` (uploaded files)

## Requirements

- Python 3.8+
- Cloud SQL Proxy running (for orders)
- GCS credentials configured

## Help

```bash
python run.py --help
python run.py download --help
python run.py oem --help
```
