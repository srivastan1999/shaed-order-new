"""
FastAPI Backend for SHAED Order ELT
Provides API endpoints to query BigQuery and return results for frontend display
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
from pathlib import Path

from .services.bigquery_service import BigQueryService
from .services.processing_service import ProcessingService
from .models.response_models import FieldComparisonResponse, ErrorResponse

# Initialize FastAPI app
app = FastAPI(
    title="SHAED Order ELT API",
    description="API for querying Ford order field comparisons from BigQuery",
    version="1.0.0"
)

# Configure CORS
# Get allowed origins from environment variable or use defaults
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001"  # Default for development
).split(",")

# Add Vercel preview and production URLs if provided
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")

vercel_production_url = os.getenv("VERCEL_PRODUCTION_URL")
if vercel_production_url:
    allowed_origins.append(vercel_production_url)

# Clean up origins (remove empty strings and strip whitespace)
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (lazy initialization for processing service to handle errors gracefully)
bq_service = BigQueryService()
processing_service = None  # Will be initialized on first use


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "SHAED Order ELT API",
        "version": "1.0.0",
        "endpoints": {
            "field_comparison": "/api/ford-field-comparison",
            "process_date": "/api/ford-process-date",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test BigQuery connection
        bq_service.test_connection()
        return {"status": "healthy", "bigquery": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get(
    "/api/ford-field-comparison",
    response_model=FieldComparisonResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}}
)
async def get_ford_field_comparison(
    old_date: str = Query(..., description="Old date in YYYY-MM-DD format (e.g., 2025-11-07)"),
    new_date: str = Query(..., description="New date in YYYY-MM-DD format (e.g., 2025-11-10)"),
    limit: Optional[int] = Query(None, description="Limit number of results (optional)"),
    offset: Optional[int] = Query(0, description="Offset for pagination (default: 0)"),
    auto_fetch: bool = Query(True, description="Automatically download and process missing dates")
):
    """
    Get Ford order field comparisons between two dates
    
    Returns field changes between two versions of ford_oem_orders table.
    Shows which fields changed and their old/new values.
    
    If auto_fetch is True (default), automatically downloads and processes
    missing dates from GCS before running the comparison.
    """
    try:
        # Validate date formats
        try:
            datetime.strptime(old_date, "%Y-%m-%d")
            datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD format (e.g., 2025-11-07)"
            )
        
        # Check and auto-fetch missing dates if enabled
        if auto_fetch:
            missing_dates = []
            fetch_results = {}
            
            # Check old_date
            if not bq_service.check_date_exists(old_date):
                missing_dates.append(old_date)
                fetch_result = bq_service.ensure_ford_date_available(old_date)
                fetch_results[old_date] = fetch_result
            
            # Check new_date
            if not bq_service.check_date_exists(new_date):
                missing_dates.append(new_date)
                fetch_result = bq_service.ensure_ford_date_available(new_date)
                fetch_results[new_date] = fetch_result
            
            # If we fetched data, wait a moment for BigQuery to update
            if missing_dates:
                import time
                time.sleep(3)  # Give BigQuery time to process the upload
        
        # Execute query
        results = await bq_service.get_ford_field_comparison(
            old_date=old_date,
            new_date=new_date,
            limit=limit,
            offset=offset
        )
        
        # Add fetch information if dates were auto-fetched
        if auto_fetch and missing_dates:
            results["auto_fetched_dates"] = missing_dates
            results["fetch_results"] = fetch_results
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing query: {str(e)}"
        )


@app.get("/api/ford-field-comparison/stats")
async def get_ford_field_comparison_stats(
    old_date: str = Query(..., description="Old date in YYYY-MM-DD format"),
    new_date: str = Query(..., description="New date in YYYY-MM-DD format")
):
    """
    Get statistics about field comparisons
    
    Returns summary statistics like total changes, unique orders affected, etc.
    """
    try:
        # Validate date formats
        try:
            datetime.strptime(old_date, "%Y-%m-%d")
            datetime.strptime(new_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD format (e.g., 2025-11-07)"
            )
        
        stats = await bq_service.get_ford_field_comparison_stats(
            old_date=old_date,
            new_date=new_date
        )
        
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting statistics: {str(e)}"
        )


@app.get("/api/ford-process-date")
async def process_ford_date(
    date: str = Query(..., description="Date in YYYY-MM-DD format (e.g., 2025-11-07)"),
    return_data: bool = Query(True, description="Whether to return processed data from BigQuery"),
    limit: Optional[int] = Query(None, description="Limit number of results to return (optional)")
):
    """
    Process Ford data for a specific date: Check if exists → If not, Download → Process → Upload to BigQuery → Return Data
    
    This endpoint:
    1. Checks if data already exists in BigQuery for the date
    2. If exists: Returns the existing data immediately
    3. If not exists:
       - Downloads the Ford Excel file for the specified date from GCS
       - Processes and converts it to CSV
       - Uploads to GCS and loads into BigQuery
    4. Returns the processed data from BigQuery
    
    Args:
        date: Date in YYYY-MM-DD format
        return_data: Whether to return the processed data (default: True)
        limit: Optional limit on number of results
        
    Returns:
        Dictionary with processing status and data
    """
    try:
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD format (e.g., 2025-11-07)"
            )
        
        # Initialize processing service if not already initialized
        global processing_service
        if processing_service is None:
            try:
                processing_service = ProcessingService()
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to initialize processing service: {str(e)}"
                )
        
        # Process the date (run in thread pool since it's CPU/IO bound)
        import asyncio
        result = await asyncio.to_thread(
            processing_service.process_and_upload_date,
            date=date,
            return_data=return_data,
            limit=limit
        )
        
        # Check if processing was successful
        if not result.get("success", False):
            # Return result with error status
            return JSONResponse(
                status_code=200,  # Still 200 because we got a response, just processing failed
                content=result
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing date: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment or use default
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)

