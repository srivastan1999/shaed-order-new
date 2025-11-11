"""
BigQuery Service
Handles all BigQuery queries and data retrieval
"""

from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import os
from pathlib import Path
from datetime import datetime

# Import config from parent project
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from shared.config import DOWNLOAD_PROJECT_ID
from data_extraction import OEMDownloader
from processing.processors import OEM_PROCESSORS


class BigQueryService:
    """Service for executing BigQuery queries"""
    
    def __init__(self, project_id: Optional[str] = None):
        """
        Initialize BigQuery service
        
        Args:
            project_id: GCP project ID (default: from config)
        """
        self.project_id = project_id or DOWNLOAD_PROJECT_ID
        if not self.project_id:
            raise ValueError("PROJECT_ID must be set in environment variables or .env file")
        
        self.client = bigquery.Client(project=self.project_id)
        self.dataset_id = "shaed_elt"
        
        # Load SQL query template
        self._load_query_template()
    
    def _load_query_template(self):
        """Load the SQL query template from file (parameterized version)"""
        # SQL files are now in backend/queries/ directory
        queries_dir = Path(__file__).parent.parent / "queries"
        
        # Try parameterized version first, fallback to original
        query_file = queries_dir / "ford_orders_field_comparison_parameterized.sql"
        
        if not query_file.exists():
            # Fallback to original file
            query_file = queries_dir / "ford_orders_field_comparison.sql"
            if not query_file.exists():
                raise FileNotFoundError(f"Query file not found: {query_file}")
        
        with open(query_file, 'r') as f:
            self.query_template = f.read()
            self.use_parameters = "@old_date" in self.query_template and "@new_date" in self.query_template
    
    def _build_query_config(self, old_date: str, new_date: str):
        """
        Build BigQuery query job config with parameterized dates
        
        Args:
            old_date: Old date in YYYY-MM-DD format
            new_date: New date in YYYY-MM-DD format
            
        Returns:
            Tuple of (query_string, QueryJobConfig)
        """
        from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
        
        query = self.query_template
        
        if self.use_parameters:
            # Use parameterized query
            job_config = QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("old_date", "DATE", old_date),
                    ScalarQueryParameter("new_date", "DATE", new_date),
                ]
            )
            return query, job_config
        else:
            # Fallback: string replacement for non-parameterized queries
            query = query.replace("'2025-11-07'", f"'{old_date}'")
            query = query.replace("'2025-11-10'", f"'{new_date}'")
            query = query.replace("'2025-11-07' AS old_date", f"'{old_date}' AS old_date")
            query = query.replace("'2025-11-10' AS new_date", f"'{new_date}' AS new_date")
            return query, QueryJobConfig()
    
    def test_connection(self):
        """Test BigQuery connection"""
        try:
            # Try to list datasets
            datasets = list(self.client.list_datasets(max_results=1))
            return True
        except Exception as e:
            raise Exception(f"BigQuery connection failed: {str(e)}")
    
    async def get_ford_field_comparison(
        self,
        old_date: str,
        new_date: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Execute Ford field comparison query
        
        Args:
            old_date: Old date in YYYY-MM-DD format
            new_date: New date in YYYY-MM-DD format
            limit: Optional limit on number of results
            offset: Offset for pagination
            
        Returns:
            Dictionary with results and metadata
        """
        # Build query and config with parameters
        query, job_config = self._build_query_config(old_date, new_date)
        
        # Remove trailing semicolon if present (for adding LIMIT/OFFSET)
        query = query.rstrip().rstrip(';')
        
        # Add pagination if needed
        if limit is not None:
            query += f"\nLIMIT {limit}"
        if offset > 0:
            query += f"\nOFFSET {offset}"
        
        try:
            # Execute query with parameterized config
            query_job = self.client.query(query, job_config=job_config)
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
            
            # Get total count by executing the same query without limit/offset
            # We'll count the rows we already fetched, or execute a simpler count
            # For efficiency, we can count the rows we already have if no limit was applied
            if limit is None:
                total_count = len(rows)
            else:
                # Execute a count query (simpler version)
                count_query, count_config = self._build_query_config(old_date, new_date)
                count_query = count_query.rstrip().rstrip(';')
                count_query = f"SELECT COUNT(*) as total FROM ({count_query})"
                
                try:
                    count_job = self.client.query(count_query, job_config=count_config)
                    total_count = next(count_job.result()).total
                except Exception:
                    # Fallback: use the number of rows we fetched
                    total_count = len(rows)
            
            return {
                "data": rows,
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "old_date": old_date,
                "new_date": new_date
            }
            
        except NotFound as e:
            raise Exception(f"Table or dataset not found: {str(e)}")
        except Exception as e:
            raise Exception(f"Query execution failed: {str(e)}")
    
    async def get_ford_field_comparison_stats(
        self,
        old_date: str,
        new_date: str
    ) -> Dict[str, Any]:
        """
        Get statistics about field comparisons
        
        Args:
            old_date: Old date in YYYY-MM-DD format
            new_date: New date in YYYY-MM-DD format
            
        Returns:
            Dictionary with statistics
        """
        # Build base query and config with parameters
        base_query, job_config = self._build_query_config(old_date, new_date)
        base_query = base_query.rstrip().rstrip(';')
        
        # Create stats query
        stats_query = f"""
        WITH field_changes AS (
            {base_query}
        )
        SELECT 
            Field_Name,
            COUNT(*) as change_count
        FROM field_changes
        GROUP BY Field_Name
        ORDER BY change_count DESC
        """
        
        try:
            # Execute stats query with parameterized config
            query_job = self.client.query(stats_query, job_config=job_config)
            results = query_job.result()
            
            # Get field-level stats
            field_stats = []
            for row in results:
                field_stats.append({
                    "field_name": row.Field_Name,
                    "change_count": row.change_count
                })
            
            # Get overall stats
            total_changes = sum(stat["change_count"] for stat in field_stats)
            
            # Get unique orders count
            unique_orders_query = f"""
            WITH field_changes AS (
                {base_query}
            )
            SELECT COUNT(DISTINCT Order_Number) as unique_orders
            FROM field_changes
            """
            
            try:
                unique_orders_job = self.client.query(unique_orders_query, job_config=job_config)
                unique_orders = next(unique_orders_job.result()).unique_orders
            except Exception:
                # Fallback: estimate from field stats (not perfect but better than error)
                unique_orders = len(field_stats)
            
            return {
                "total_changes": total_changes,
                "unique_orders_affected": unique_orders,
                "unique_fields_changed": len(field_stats),
                "field_statistics": field_stats,
                "old_date": old_date,
                "new_date": new_date
            }
            
        except Exception as e:
            raise Exception(f"Stats query failed: {str(e)}")
    
    def check_date_exists(self, date: str) -> bool:
        """
        Check if a date exists in the ford_oem_orders table
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            True if date exists, False otherwise
        """
        try:
            query = f"""
            SELECT COUNT(*) as count
            FROM `{self.project_id}.{self.dataset_id}.ford_oem_orders`
            WHERE _source_file_date = @date
            LIMIT 1
            """
            
            from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
            
            job_config = QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("date", "DATE", date),
                ]
            )
            
            query_job = self.client.query(query, job_config=job_config)
            result = next(query_job.result())
            return result.count > 0
            
        except Exception as e:
            # If table doesn't exist or error, return False
            return False
    
    def ensure_ford_date_available(self, date: str) -> Dict[str, Any]:
        """
        Ensure Ford data for a date is available in BigQuery.
        If not, automatically download, process, and upload it.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with status information
        """
        from datetime import datetime as dt
        
        # Check if date already exists
        if self.check_date_exists(date):
            return {
                "status": "exists",
                "message": f"Date {date} already exists in BigQuery",
                "action_taken": None
            }
        
        # Convert YYYY-MM-DD to MM.DD.YYYY format for download
        try:
            date_obj = dt.strptime(date, "%Y-%m-%d")
            download_date = date_obj.strftime("%m.%d.%Y")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD")
        
        result = {
            "status": "processing",
            "message": f"Date {date} not found. Downloading and processing...",
            "action_taken": [],
            "date": date,
            "download_date": download_date
        }
        
        try:
            # Step 1: Download
            result["action_taken"].append("download")
            downloader = OEMDownloader("ford")
            downloaded = downloader.download_for_dates([download_date])
            
            if not downloaded:
                return {
                    "status": "error",
                    "message": f"Could not download Ford data for {date}",
                    "action_taken": result["action_taken"],
                    "error": "No files downloaded from GCS"
                }
            
            # Step 2: Process
            result["action_taken"].append("process")
            processor = OEM_PROCESSORS["ford"]()
            
            processed_count = 0
            for excel_file in downloaded:
                try:
                    processor.convert_excel_to_csv(
                        excel_file=excel_file,
                        upload_to_gcs_flag=True  # Always upload to GCS and BigQuery
                    )
                    processed_count += 1
                except Exception as e:
                    result["action_taken"].append(f"process_error: {str(e)}")
                    continue
            
            if processed_count == 0:
                return {
                    "status": "error",
                    "message": f"Could not process Ford data for {date}",
                    "action_taken": result["action_taken"],
                    "error": "No files processed successfully"
                }
            
            # Step 3: Verify it's now in BigQuery
            # Wait a moment for BigQuery to update
            import time
            time.sleep(2)
            
            if self.check_date_exists(date):
                result["status"] = "success"
                result["message"] = f"Successfully downloaded, processed, and uploaded {date}"
                result["action_taken"].append("upload")
                result["files_processed"] = processed_count
            else:
                result["status"] = "warning"
                result["message"] = f"Processed {date} but may not be fully available in BigQuery yet"
                result["files_processed"] = processed_count
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing {date}: {str(e)}",
                "action_taken": result["action_taken"],
                "error": str(e)
            }

