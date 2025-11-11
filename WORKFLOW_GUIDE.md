# Daily Workflow Guide

## Quick Start

### Terminal 1: Start Proxy
```bash
./start_proxy.sh
```
Keep this running!

### Terminal 2: Run Workflow
```bash
./complete_workflow.sh
```

Done! Files are cleaned and uploaded to GCS.

---

## Changing Dates

Edit `.env` file:
```bash
DATE1=11.05.2025
DATE2=11.06.2025
```

Then run:
```bash
./complete_workflow.sh
```

---

## Individual Tasks

```bash
# Just download
python run.py download ford --from-env

# Just orders
python run.py orders

# Just Ford processing
python run.py oem ford

# Download specific date
python run.py download ford --date 11.05.2025
```

---

## Troubleshooting

### "Connection refused"
→ Start Cloud SQL Proxy: `./start_proxy.sh`

### "No files found"
→ Check dates in `.env` are correct (MM.DD.YYYY format)

### "No password supplied"
→ Check `DB_PASSWORD` in `.env` file

---

## What Gets Created

### Downloaded
- `data/input/Ford Dealer Report*.xlsx`

### Output
- `data/output/v_orders_api_bigquery_YYYYMMDD_HHMMSS.csv`
- `data/output/Ford_Dealer_Report_clean_YYYYMMDD_HHMMSS.csv`

### GCS Upload
- `gs://shaed-elt-csv/order_view_api/`
