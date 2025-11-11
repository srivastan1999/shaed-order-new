"""
Processing Service
Handles data processing pipeline: Download → Process → Upload to BigQuery → Return Data
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import re

# Add parent project to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from data_extraction import OEMDownloader
from processing.processors import OEM_PROCESSORS
from processing.bigquery_loader import BigQueryLoader
from google.cloud import bigquery
from google.cloud.exceptions import NotFound


class ProcessingService:
    """Service for processing Ford data for a specific date"""
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize Processing Service
        
        Args:
            project_id: GCP project ID (default: from config)
        """
        from shared.config import DOWNLOAD_PROJECT_ID
        self.project_id = project_id or DOWNLOAD_PROJECT_ID
        if not self.project_id:
            raise ValueError("PROJECT_ID must be set in environment variables or .env file")
        
        self.dataset_id = "shaed_elt"
        self.client = bigquery.Client(project=self.project_id)
    
    def _convert_date_format(self, date_str: str) -> str:
        """
        Convert date from YYYY-MM-DD to MM.DD.YYYY format
        
        Args:
            date_str: Date in YYYY-MM-DD format
            
        Returns:
            Date in MM.DD.YYYY format
        """
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%m.%d.%Y")
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected YYYY-MM-DD")
    
    def _check_data_exists(self, date: str) -> tuple[bool, int]:
        """
        Check if data already exists in BigQuery for the given date
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Tuple of (exists: bool, row_count: int)
        """
        try:
            check_query = f"""
            SELECT COUNT(*) as row_count
            FROM `{self.project_id}.{self.dataset_id}.ford_oem_orders`
            WHERE _source_file_date = '{date}'
            """
            query_job = self.client.query(check_query)
            row_count = next(query_job.result()).row_count
            return (row_count > 0, row_count)
        except Exception as e:
            print(f"Error checking if data exists: {str(e)}")
            return (False, 0)
    
    def _fetch_data_from_bigquery(
        self,
        date: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch data from BigQuery for a given date
        
        Args:
            date: Date in YYYY-MM-DD format
            limit: Optional limit on number of results
            
        Returns:
            Dictionary with rows and metadata
        """
        data_query = f"""
        SELECT *
        FROM `{self.project_id}.{self.dataset_id}.ford_oem_orders`
        WHERE _source_file_date = '{date}'
        ORDER BY Order_Number, Body_Code, Model_Year
        """
        
        if limit is not None:
            data_query += f"\nLIMIT {limit}"
        
        try:
            query_job = self.client.query(data_query)
            results = query_job.result()
            
            # Convert to list of dictionaries
            rows = []
            for row in results:
                row_dict = {}
                for key, value in row.items():
                    # Convert datetime/timestamp to string for JSON serialization
                    if isinstance(value, (datetime,)):
                        row_dict[key] = value.isoformat()
                    else:
                        row_dict[key] = value
                rows.append(row_dict)
            
            # Get total count
            count_query = f"""
            SELECT COUNT(*) as total
            FROM `{self.project_id}.{self.dataset_id}.ford_oem_orders`
            WHERE _source_file_date = '{date}'
            """
            count_job = self.client.query(count_query)
            total_count = next(count_job.result()).total
            
            return {
                "rows": rows,
                "total": total_count,
                "limit": limit,
                "source_file_date": date
            }
        except Exception as e:
            raise Exception(f"Error fetching data from BigQuery: {str(e)}")
    
    def process_and_upload_date(
        self,
        date: str,
        return_data: bool = True,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process Ford data for a specific date: Check if exists → If not, Download → Process → Upload to BigQuery → Return Data
        
        Args:
            date: Date in YYYY-MM-DD format
            return_data: Whether to return the processed data from BigQuery
            limit: Optional limit on number of results to return
            
        Returns:
            Dictionary with processing status and optionally the data
        """
        # Convert date format
        date_mm_dd_yyyy = self._convert_date_format(date)
        
        result = {
            "date": date,
            "date_formatted": date_mm_dd_yyyy,
            "steps": {},
            "success": False,
            "data": None,
            "data_already_exists": False
        }
        
        try:
            # Step 0: Check if data already exists in BigQuery
            result["steps"]["check_existing"] = {"status": "in_progress", "message": ""}
            data_exists, existing_row_count = self._check_data_exists(date)
            
            if data_exists:
                result["data_already_exists"] = True
                result["steps"]["check_existing"] = {
                    "status": "success",
                    "message": f"Data already exists in BigQuery: {existing_row_count} rows",
                    "row_count": existing_row_count
                }
                
                # If data exists, just fetch and return it
                if return_data:
                    result["steps"]["fetch_data"] = {"status": "in_progress", "message": ""}
                    try:
                        result["data"] = self._fetch_data_from_bigquery(date, limit)
                        result["steps"]["fetch_data"] = {
                            "status": "success",
                            "message": f"Fetched {len(result['data']['rows'])} rows from BigQuery",
                            "total_rows": result["data"]["total"]
                        }
                    except Exception as e:
                        result["steps"]["fetch_data"] = {
                            "status": "failed",
                            "message": f"Error fetching data: {str(e)}"
                        }
                        result["success"] = False
                        return result
                
                result["success"] = True
                return result
            
            # Data doesn't exist, proceed with full processing pipeline
            result["steps"]["check_existing"] = {
                "status": "success",
                "message": "No existing data found, proceeding with processing"
            }
            
            # Step 1: Check if local CSV exists first
            from pathlib import Path
            from shared.config import OUTPUT_DIR
            
            date_yyyymmdd = date.replace("-", "")
            csv_pattern = f"Ford_Dealer_Report_clean_{date_yyyymmdd}.csv"
            existing_csv = Path(OUTPUT_DIR) / csv_pattern
            
            if existing_csv.exists():
                # Local CSV exists - use it instead of downloading
                result["steps"]["download"] = {
                    "status": "skipped",
                    "message": f"Local CSV file exists: {existing_csv.name}. Using local file instead of downloading from GCS.",
                    "file": str(existing_csv)
                }
                output_csv = existing_csv
                
                # Skip processing step since file already exists
                result["steps"]["process"] = {
                    "status": "skipped",
                    "message": f"Using existing processed file: {existing_csv.name}",
                    "output_file": str(existing_csv)
                }
                
                # Check if this CSV needs to be uploaded to BigQuery
                # If data doesn't exist in BigQuery, try to upload the existing CSV
                data_exists, existing_row_count = self._check_data_exists(date)
                if not data_exists:
                    result["steps"]["bigquery_upload"] = {"status": "in_progress", "message": ""}
                    try:
                        from processing.bigquery_loader import BigQueryLoader
                        loader = BigQueryLoader()
                        upload_success = loader.load_ford_oem_csv_from_local(existing_csv)
                        if upload_success:
                            result["steps"]["bigquery_upload"] = {
                                "status": "success",
                                "message": f"Uploaded existing CSV to BigQuery",
                                "source_file_date": date
                            }
                        else:
                            result["steps"]["bigquery_upload"] = {
                                "status": "warning",
                                "message": f"Failed to upload existing CSV to BigQuery",
                                "source_file_date": date
                            }
                    except Exception as e:
                        result["steps"]["bigquery_upload"] = {
                            "status": "warning",
                            "message": f"Error uploading existing CSV: {str(e)}",
                            "source_file_date": date
                        }
                else:
                    result["steps"]["bigquery_upload"] = {
                        "status": "skipped",
                        "message": f"Data already exists in BigQuery ({existing_row_count} rows)",
                        "row_count": existing_row_count,
                        "source_file_date": date
                    }
            else:
                # Local CSV doesn't exist - download from GCS
                result["steps"]["download"] = {"status": "in_progress", "message": ""}
                downloader = OEMDownloader("ford")
                downloaded = downloader.download_for_dates([date_mm_dd_yyyy])
                
                if not downloaded:
                    # No file found in GCS - still try to show data from BigQuery if available
                    result["steps"]["download"] = {
                        "status": "failed",
                        "message": f"No file found in GCS for date {date_mm_dd_yyyy} and no local CSV file exists"
                    }
                    result["steps"]["process"] = {
                        "status": "skipped",
                        "message": "Skipped - no source file available"
                    }
                    
                    # Even if no file, try to return data from BigQuery if it exists
                    if return_data:
                        result["steps"]["fetch_data"] = {"status": "in_progress", "message": ""}
                        try:
                            result["data"] = self._fetch_data_from_bigquery(date, limit)
                            result["steps"]["fetch_data"] = {
                                "status": "success",
                                "message": f"Fetched {len(result['data']['rows'])} rows from BigQuery (no new file processed)",
                                "total_rows": result["data"]["total"]
                            }
                            result["success"] = True  # Success if we got data from BigQuery
                        except Exception as e:
                            result["steps"]["fetch_data"] = {
                                "status": "failed",
                                "message": f"No data available: {str(e)}"
                            }
                    
                    return result
                else:
                    # File was downloaded successfully from GCS
                    downloaded_file = downloaded[0]
                    result["steps"]["download"] = {
                        "status": "success",
                        "message": f"Downloaded from GCS: {downloaded_file.name}",
                        "file": str(downloaded_file)
                    }
                    
                    # Step 2: Process
                    result["steps"]["process"] = {"status": "in_progress", "message": ""}
                    processor = OEM_PROCESSORS["ford"]()
                    
                    # Process the downloaded file
                    output_csv = processor.convert_excel_to_csv(
                        excel_file=downloaded_file,
                        upload_to_gcs_flag=True  # Always upload to GCS
                    )
                    
                    result["steps"]["process"] = {
                        "status": "success",
                        "message": f"Processed: {output_csv.name}",
                        "output_file": str(output_csv)
                    }
            
            # Step 3: Upload to BigQuery (should be automatic, but verify)
            # Only initialize if not already set (for existing CSV case, it's already handled)
            if "bigquery_upload" not in result["steps"]:
                result["steps"]["bigquery_upload"] = {"status": "in_progress", "message": ""}
            
            # Extract date from output filename to check BigQuery
            date_match = re.search(r'(\d{4})(\d{2})(\d{2})', output_csv.name)
            if date_match:
                year, month, day = date_match.groups()
                source_file_date = f"{year}-{month}-{day}"
                
                # Wait a bit for BigQuery job to complete (processor should wait, but double-check)
                import time
                time.sleep(2)
                
                # Verify data exists in BigQuery (check multiple times with retries)
                max_retries = 5
                retry_delay = 3
                row_count = 0
                
                for attempt in range(max_retries):
                    try:
                        verify_query = f"""
                        SELECT COUNT(*) as row_count
                        FROM `{self.project_id}.{self.dataset_id}.ford_oem_orders`
                        WHERE _source_file_date = '{source_file_date}'
                        """
                        query_job = self.client.query(verify_query)
                        row_count = next(query_job.result()).row_count
                        
                        if row_count > 0:
                            break  # Data found, exit retry loop
                        elif attempt < max_retries - 1:
                            # Wait before retrying
                            time.sleep(retry_delay)
                    except Exception as e:
                        if attempt < max_retries - 1:
                            time.sleep(retry_delay)
                            continue
                        else:
                            result["steps"]["bigquery_upload"] = {
                                "status": "warning",
                                "message": f"Could not verify BigQuery upload: {str(e)}"
                            }
                            break
                
                # Set final status
                if row_count > 0:
                    result["steps"]["bigquery_upload"] = {
                        "status": "success",
                        "message": f"Data uploaded to BigQuery: {row_count} rows",
                        "row_count": row_count,
                        "source_file_date": source_file_date
                    }
                else:
                    result["steps"]["bigquery_upload"] = {
                        "status": "warning",
                        "message": f"BigQuery upload may have failed - 0 rows found after {max_retries} attempts. Check CSV file and BigQuery logs.",
                        "row_count": 0,
                        "source_file_date": source_file_date,
                        "csv_file": str(output_csv),
                        "csv_size_bytes": output_csv.stat().st_size if output_csv.exists() else 0
                    }
            else:
                result["steps"]["bigquery_upload"] = {
                    "status": "warning",
                    "message": "Could not extract date from filename to verify upload"
                }
            
            # Step 4: Return data if requested
            if return_data:
                result["steps"]["fetch_data"] = {"status": "in_progress", "message": ""}
                
                # Query data from BigQuery using the date we already have
                try:
                    result["data"] = self._fetch_data_from_bigquery(date, limit)
                    result["steps"]["fetch_data"] = {
                        "status": "success",
                        "message": f"Fetched {len(result['data']['rows'])} rows from BigQuery",
                        "total_rows": result["data"]["total"]
                    }
                except Exception as e:
                    result["steps"]["fetch_data"] = {
                        "status": "failed",
                        "message": f"Error fetching data: {str(e)}"
                    }
            
            result["success"] = True
            return result
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            result["steps"]["error"] = {
                "status": "failed",
                "message": str(e),
                "traceback": error_trace
            }
            result["success"] = False
            # Log the full error for debugging
            print(f"ERROR in process_and_upload_date: {str(e)}")
            print(error_trace)
            return result

