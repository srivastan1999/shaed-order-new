"""
FastAPI Backend for SHAED Order ELT
Provides API endpoints to query BigQuery and return results for frontend display
"""

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
import os
from pathlib import Path
import logging

from .services.bigquery_service import BigQueryService
from .services.processing_service import ProcessingService
from .models.response_models import FieldComparisonResponse, ErrorResponse

# Initialize FastAPI app
app = FastAPI(
    title="SHAED Order ELT API",
    description="API for querying Ford order field comparisons from BigQuery",
    version="1.0.0"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Origin: {request.headers.get('origin', 'N/A')}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response

# Configure CORS
# Get allowed origins from environment variable or use defaults
# For development, allow all localhost origins
is_development = os.getenv("ENVIRONMENT", "development").lower() == "development"

if is_development:
    # In development, allow all localhost origins and common dev ports
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://localhost:3002",
        "http://localhost:3003",
    ]
    # Also add any from environment
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    if env_origins:
        allowed_origins.extend([origin.strip() for origin in env_origins.split(",") if origin.strip()])
else:
    # In production, use strict origin list
    allowed_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://localhost:3001"
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

logger.info(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Initialize services (lazy initialization to handle errors gracefully)
bq_service = None
processing_service = None  # Will be initialized on first use

def get_bq_service():
    """Lazy initialization of BigQuery service"""
    global bq_service
    if bq_service is None:
        try:
            bq_service = BigQueryService()
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery service: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to initialize BigQuery service: {str(e)}"
            )
    return bq_service


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

@app.get("/api/test")
async def test_endpoint():
    """Simple test endpoint that doesn't require BigQuery"""
    import os
    return {
        "status": "ok",
        "message": "API is working",
        "env_check": {
            "PROJECT_ID": "SET" if os.getenv("PROJECT_ID") else "NOT SET",
            "DOWNLOAD_PROJECT_ID": "SET" if os.getenv("DOWNLOAD_PROJECT_ID") else "NOT SET",
            "GOOGLE_APPLICATION_CREDENTIALS_JSON": "SET" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON") else "NOT SET",
            "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "NOT SET")
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    import os
    env_status = {
        "PROJECT_ID": os.getenv("PROJECT_ID", "NOT SET"),
        "DOWNLOAD_PROJECT_ID": os.getenv("DOWNLOAD_PROJECT_ID", "NOT SET"),
        "GOOGLE_APPLICATION_CREDENTIALS": os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "NOT SET"),
        "GOOGLE_APPLICATION_CREDENTIALS_JSON": "SET" if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON") else "NOT SET"
    }
    
    try:
        # Test BigQuery connection
        bq_service = get_bq_service()
        bq_service.test_connection()
        return {
            "status": "healthy", 
            "bigquery": "connected",
            "environment": env_status
        }
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Health check failed: {e}")
        logger.error(error_trace)
        return {
            "status": "unhealthy", 
            "error": str(e),
            "environment": env_status,
            "traceback": error_trace
        }


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
    auto_fetch: bool = Query(True, description="Automatically download and process missing dates"),
    query_type: str = Query("db_comparison", description="Type of query: 'db_comparison' (Ford DB Comparison) or 'field_comparison' (Ford Comparison)"),
    db_orders_date: Optional[str] = Query(None, description="Date for db_orders table selection in YYYY-MM-DD format (e.g., 2025-11-10). Only used for db_comparison query type. If not provided, uses new_date.")
):
    """
    Get Ford order field comparisons between two dates
    
    Returns field changes between two versions of ford_oem_orders table.
    Shows which fields changed and their old/new values.
    
    Query types:
    - "db_comparison": Uses ford_orders_db_comarision.sql - compares with db_orders table (Ford DB Comparison)
    - "field_comparison": Uses ford_orders_field_comparison_parameterized.sql - regular field comparison (Ford Comparison)
    
    If auto_fetch is True (default), automatically downloads and processes
    missing dates from GCS before running the comparison.
    """
    # Log request
    request_params = {
        "old_date": old_date,
        "new_date": new_date,
        "limit": limit,
        "offset": offset,
        "auto_fetch": auto_fetch,
        "query_type": query_type,
        "db_orders_date": db_orders_date
    }
    logger.info(f"=== FORD FIELD COMPARISON REQUEST ===")
    logger.info(f"Endpoint: /api/ford-field-comparison")
    logger.info(f"Request Parameters: {request_params}")
    
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
        missing_dates = []
        fetch_results = {}
        
        if auto_fetch:
            logger.info(f"Auto-fetch enabled: Checking for missing dates...")
            bq = get_bq_service()
            # Check old_date (for ford_oem_orders)
            try:
                logger.info(f"Checking if old_date {old_date} exists in ford_oem_orders...")
                if not bq.check_date_exists(old_date):
                    logger.info(f"old_date {old_date} not found. Auto-fetching...")
                    missing_dates.append(old_date)
                    fetch_result = bq.ensure_ford_date_available(old_date)
                    fetch_results[old_date] = fetch_result
                    logger.info(f"Auto-fetch result for {old_date}: {fetch_result.get('status', 'unknown')}")
                else:
                    logger.info(f"old_date {old_date} already exists in BigQuery")
            except Exception as e:
                logger.warning(f"Error checking/fetching old_date {old_date}: {str(e)}")
                # Continue anyway - the query might still work
            
            # Check new_date (for ford_oem_orders)
            try:
                logger.info(f"Checking if new_date {new_date} exists in ford_oem_orders...")
                if not bq.check_date_exists(new_date):
                    logger.info(f"new_date {new_date} not found. Auto-fetching...")
                    missing_dates.append(new_date)
                    fetch_result = bq.ensure_ford_date_available(new_date)
                    fetch_results[new_date] = fetch_result
                    logger.info(f"Auto-fetch result for {new_date}: {fetch_result.get('status', 'unknown')}")
                else:
                    logger.info(f"new_date {new_date} already exists in BigQuery")
            except Exception as e:
                logger.warning(f"Error checking/fetching new_date {new_date}: {str(e)}")
                # Continue anyway - the query might still work
            
            # For DB comparison, also check db_orders_date
            if query_type == "db_comparison":
                # Use db_orders_date if provided, otherwise use new_date
                date_to_check = db_orders_date if db_orders_date else new_date
                try:
                    logger.info(f"Checking if db_orders table exists for date {date_to_check}...")
                    if not bq.check_db_orders_table_exists(date_to_check):
                        logger.info(f"db_orders table for {date_to_check} not found. Auto-fetching...")
                        missing_dates.append(f"db_orders_{date_to_check}")
                        fetch_result = bq.ensure_db_orders_date_available(date_to_check)
                        fetch_results[f"db_orders_{date_to_check}"] = fetch_result
                        logger.info(f"Auto-fetch result for db_orders_{date_to_check}: {fetch_result.get('status', 'unknown')}")
                    else:
                        logger.info(f"db_orders table for {date_to_check} already exists in BigQuery")
                except Exception as e:
                    logger.warning(f"Error checking/fetching db_orders_date {date_to_check}: {str(e)}")
                    # Continue anyway - the query might still work
            
            # If we fetched data, wait a moment for BigQuery to update
            if missing_dates:
                logger.info(f"Waiting 3 seconds for BigQuery to process {len(missing_dates)} uploaded date(s)...")
                import time
                time.sleep(3)  # Give BigQuery time to process the upload
                logger.info(f"Wait complete. Proceeding with query execution.")
            else:
                logger.info(f"All required dates are available. No auto-fetch needed.")
        
        # Validate query_type
        if query_type not in ["db_comparison", "field_comparison"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid query_type. Must be 'db_comparison' or 'field_comparison'"
            )
        
        # Validate db_orders_date if provided
        if db_orders_date:
            try:
                datetime.strptime(db_orders_date, "%Y-%m-%d")
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid db_orders_date format. Use YYYY-MM-DD format (e.g., 2025-11-10)"
                )
        
        # Execute query
        logger.info(f"Executing BigQuery query with query_type={query_type}")
        start_time = datetime.now()
        
        results = await get_bq_service().get_ford_field_comparison(
            old_date=old_date,
            new_date=new_date,
            limit=limit,
            offset=offset,
            query_type=query_type,
            db_orders_date=db_orders_date
        )
        
        query_duration = (datetime.now() - start_time).total_seconds()
        
        # Add fetch information if dates were auto-fetched
        if auto_fetch and missing_dates:
            results["auto_fetched_dates"] = missing_dates
            results["fetch_results"] = fetch_results
        
        # Log response
        response_summary = {
            "status": "success",
            "total_rows": results.get("total", 0),
            "data_rows": len(results.get("data", [])),
            "offset": results.get("offset", 0),
            "query_duration_seconds": round(query_duration, 2),
            "auto_fetched_dates": missing_dates if auto_fetch and missing_dates else None
        }
        logger.info(f"=== FORD FIELD COMPARISON RESPONSE ===")
        logger.info(f"Response Summary: {response_summary}")
        logger.info(f"Query executed successfully in {query_duration:.2f} seconds")
        
        return results
        
    except HTTPException as e:
        # Log HTTP exceptions
        logger.error(f"=== FORD FIELD COMPARISON ERROR (HTTP {e.status_code}) ===")
        logger.error(f"Error: {e.detail}")
        raise
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        # Log the full error for debugging
        logger.error(f"=== FORD FIELD COMPARISON ERROR ===")
        logger.error(f"Error Type: {type(e).__name__}")
        logger.error(f"Error Message: {str(e)}")
        logger.error(f"Traceback:\n{error_trace}")
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
        
        stats = await get_bq_service().get_ford_field_comparison_stats(
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

