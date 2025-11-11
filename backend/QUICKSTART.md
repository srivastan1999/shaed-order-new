# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure Environment

Make sure your `.env` file has:

```env
PROJECT_ID=your-gcp-project-id
```

## 3. Start the Backend

```bash
# Option 1: Using the startup script
./start_backend.sh

# Option 2: Using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Using Python module
python -m backend.main
```

## 4. Test the API

### Using Browser
- Open: http://localhost:8000/docs (Swagger UI)
- Or: http://localhost:8000/redoc (ReDoc)

### Using curl

```bash
# Health check
curl http://localhost:8000/health

# Get field comparisons
curl "http://localhost:8000/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10&limit=10"

# Get statistics
curl "http://localhost:8000/api/ford-field-comparison/stats?old_date=2025-11-07&new_date=2025-11-10"
```

## 5. Test Frontend Example

1. Start the backend server
2. Open `backend/example_frontend.html` in your browser
3. Enter dates and click "Load Data"

**Note:** If you get CORS errors, make sure the backend is running and the API URL in the HTML file matches your backend URL.

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/api/ford-field-comparison` | GET | Get field comparisons |
| `/api/ford-field-comparison/stats` | GET | Get statistics |

## Example Response

```json
{
  "data": [
    {
      "Order_Number": "12345",
      "Body_Code": "ABC",
      "Model_Year": 2025,
      "Customer_Name": "Customer Name",
      "VIN": "VIN123",
      "Field_Name": "Estimated_Arrival_Week",
      "Old_Value": "11/24/2025",
      "New_Value": "11/29/2025",
      "old_date": "2025-11-07",
      "new_date": "2025-11-10"
    }
  ],
  "total": 150,
  "limit": 100,
  "offset": 0,
  "old_date": "2025-11-07",
  "new_date": "2025-11-10"
}
```

## Troubleshooting

### Port Already in Use
```bash
# Use a different port
uvicorn backend.main:app --port 8001
```

### BigQuery Connection Error
- Check that `PROJECT_ID` is set correctly
- Verify Google Cloud credentials are configured
- Ensure the dataset `shaed_elt` exists

### Query File Not Found
- Ensure `ford_orders_field_comparison.sql` exists in the project root
- Check file permissions

