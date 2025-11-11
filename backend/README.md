# SHAED Order ELT Backend API

FastAPI backend for querying Ford order field comparisons from BigQuery.

## Features

- RESTful API endpoints for querying BigQuery
- Field comparison queries between two dates
- Statistics and summary endpoints
- CORS enabled for frontend integration
- Automatic JSON serialization
- Error handling and validation

## Setup

### Prerequisites

1. Python 3.8+
2. Google Cloud credentials configured (via `GOOGLE_APPLICATION_CREDENTIALS` or default credentials)
3. `.env` file with `PROJECT_ID` set

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Environment Variables

Ensure your `.env` file contains:

```env
PROJECT_ID=your-gcp-project-id
API_PORT=8000  # Optional, defaults to 8000
API_HOST=0.0.0.0  # Optional, defaults to 0.0.0.0
```

## Running the Server

### Development Mode

```bash
# From project root
python -m backend.main

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Base URL

- Development: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs` (Swagger UI)
- Alternative Docs: `http://localhost:8000/redoc` (ReDoc)

### Endpoints

#### 1. Health Check

```http
GET /health
```

Returns API health status and BigQuery connection status.

**Response:**
```json
{
  "status": "healthy",
  "bigquery": "connected"
}
```

#### 2. Get Field Comparison

```http
GET /api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10
```

Returns field changes between two dates.

**Query Parameters:**
- `old_date` (required): Old date in `YYYY-MM-DD` format
- `new_date` (required): New date in `YYYY-MM-DD` format
- `limit` (optional): Limit number of results
- `offset` (optional): Offset for pagination (default: 0)

**Example Request:**
```bash
curl "http://localhost:8000/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10&limit=100"
```

**Response:**
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

#### 3. Get Statistics

```http
GET /api/ford-field-comparison/stats?old_date=2025-11-07&new_date=2025-11-10
```

Returns summary statistics about field changes.

**Query Parameters:**
- `old_date` (required): Old date in `YYYY-MM-DD` format
- `new_date` (required): New date in `YYYY-MM-DD` format

**Example Request:**
```bash
curl "http://localhost:8000/api/ford-field-comparison/stats?old_date=2025-11-07&new_date=2025-11-10"
```

**Response:**
```json
{
  "total_changes": 150,
  "unique_orders_affected": 45,
  "unique_fields_changed": 12,
  "field_statistics": [
    {
      "field_name": "Estimated_Arrival_Week",
      "change_count": 50
    },
    {
      "field_name": "Secondary_Status",
      "change_count": 30
    }
  ],
  "old_date": "2025-11-07",
  "new_date": "2025-11-10"
}
```

## Frontend Integration

### Example: Fetching Data with JavaScript

```javascript
// Fetch field comparisons
async function fetchFieldComparisons(oldDate, newDate, limit = 100, offset = 0) {
  const url = new URL('http://localhost:8000/api/ford-field-comparison');
  url.searchParams.set('old_date', oldDate);
  url.searchParams.set('new_date', newDate);
  url.searchParams.set('limit', limit);
  url.searchParams.set('offset', offset);
  
  const response = await fetch(url);
  const data = await response.json();
  return data;
}

// Usage
const results = await fetchFieldComparisons('2025-11-07', '2025-11-10');
console.log(results.data); // Array of field changes
console.log(results.total); // Total count
```

### Example: React Component

```jsx
import React, { useState, useEffect } from 'react';

function FieldComparisonTable() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function fetchData() {
      try {
        const response = await fetch(
          'http://localhost:8000/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10'
        );
        const result = await response.json();
        setData(result.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    }
    
    fetchData();
  }, []);
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <table>
      <thead>
        <tr>
          <th>Order Number</th>
          <th>Field Name</th>
          <th>Old Value</th>
          <th>New Value</th>
        </tr>
      </thead>
      <tbody>
        {data.map((row, idx) => (
          <tr key={idx}>
            <td>{row.Order_Number}</td>
            <td>{row.Field_Name}</td>
            <td>{row.Old_Value}</td>
            <td>{row.New_Value}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
```

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid parameters)
- `500`: Internal Server Error (query execution failed)

Error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Development

### Project Structure

```
backend/
├── __init__.py
├── main.py              # FastAPI application
├── models/
│   ├── __init__.py
│   └── response_models.py  # Pydantic models
├── services/
│   ├── __init__.py
│   └── bigquery_service.py  # BigQuery query service
└── README.md
```

### Adding New Endpoints

1. Add endpoint function to `backend/main.py`
2. Create response model in `backend/models/response_models.py` if needed
3. Add service method in `backend/services/bigquery_service.py` if querying BigQuery
4. Update this README with endpoint documentation

## Troubleshooting

### BigQuery Connection Issues

- Ensure `PROJECT_ID` is set in `.env`
- Verify Google Cloud credentials are configured
- Check that the dataset `shaed_elt` exists in your project

### Query Errors

- Verify the SQL query file exists: `ford_orders_field_comparison.sql`
- Check that dates are in correct format (`YYYY-MM-DD`)
- Ensure tables exist for the specified dates

### CORS Issues

- Update `allow_origins` in `main.py` to include your frontend URL
- In production, replace `["*"]` with specific allowed origins

## License

Same as parent project.

