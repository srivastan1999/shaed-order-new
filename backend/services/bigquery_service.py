"""
BigQuery Service
Handles all BigQuery queries and data retrieval
"""

from typing import List, Dict, Any, Optional
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import os
import re
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
        
        # Initialize flags
        self.is_db_comparison = False
        self.query_template = None
        self.use_parameters = False
    
    def _load_query_template(self, query_type: str = "db_comparison"):
        """
        Load the SQL query template from file
        
        Args:
            query_type: Type of query to load
                - "db_comparison": Load ford_orders_db_comarision.sql (for DB comparison)
                - "field_comparison": Load ford_orders_field_comparison_parameterized.sql (for regular comparison)
        """
        # SQL files are now in backend/queries/ directory
        queries_dir = Path(__file__).parent.parent / "queries"
        
        if query_type == "db_comparison":
            # Load DB comparison query (ford_orders_db_comparision.sql)
            query_file = queries_dir / "ford_orders_db_comparision.sql"
            if not query_file.exists():
                raise FileNotFoundError(f"DB comparison query file not found: {query_file}")
        elif query_type == "field_comparison":
            # Load regular field comparison query
            query_file = queries_dir / "ford_orders_field_comparison_parameterized.sql"
            if not query_file.exists():
                # Fallback to original file
                query_file = queries_dir / "ford_orders_field_comparison.sql"
                if not query_file.exists():
                    raise FileNotFoundError(f"Field comparison query file not found: {query_file}")
        else:
            raise ValueError(f"Unknown query_type: {query_type}. Must be 'db_comparison' or 'field_comparison'")
        
        with open(query_file, 'r') as f:
            self.query_template = f.read()
            self.use_parameters = "@old_date" in self.query_template and "@new_date" in self.query_template
            # Check if it's a DB comparison query by looking for DB comparison fields in SELECT
            self.is_db_comparison = (
                "DB_ORDERS_TABLE_PLACEHOLDER" in self.query_template or
                "Ford_Field_Name" in self.query_template or
                "DB_Orders_Value" in self.query_template or
                "Sync_Status" in self.query_template
            )
    
    def _build_query_config(self, old_date: str, new_date: str, db_orders_date: Optional[str] = None):
        """
        Build BigQuery query job config with parameterized dates
        
        Args:
            old_date: Old date in YYYY-MM-DD format
            new_date: New date in YYYY-MM-DD format
            db_orders_date: Date for db_orders table selection (YYYY-MM-DD format)
                           If None, uses new_date as fallback
            
        Returns:
            Tuple of (query_string, QueryJobConfig)
        """
        from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter
        from datetime import datetime
        
        query = self.query_template
        
        # Handle db_orders table name replacement (for DB comparison query)
        if self.is_db_comparison:
            # Use db_orders_date if provided, otherwise fallback to new_date
            date_to_use = db_orders_date if db_orders_date else new_date
            
            # Convert date (YYYY-MM-DD) to table name format (MM_DD_YYYY)
            # e.g., 2025-11-10 -> 11_10_2025
            try:
                date_obj = datetime.strptime(date_to_use, "%Y-%m-%d")
                table_suffix = date_obj.strftime("%m_%d_%Y")
                db_orders_table = f"db_orders_{table_suffix}"
                
                # Replace placeholder if it exists
                if "DB_ORDERS_TABLE_PLACEHOLDER" in query:
                    query = query.replace("DB_ORDERS_TABLE_PLACEHOLDER", db_orders_table)
                else:
                    # Replace hardcoded table name pattern (db_orders_MM_DD_YYYY)
                    query = re.sub(r"db_orders_\d{2}_\d{2}_\d{4}", db_orders_table, query)
            except ValueError:
                # If date parsing fails, try to extract from date string
                # Fallback: assume format is correct and extract parts
                parts = date_to_use.split("-")
                if len(parts) == 3:
                    table_suffix = f"{parts[1]}_{parts[2]}_{parts[0]}"
                    db_orders_table = f"db_orders_{table_suffix}"
                    if "DB_ORDERS_TABLE_PLACEHOLDER" in query:
                        query = query.replace("DB_ORDERS_TABLE_PLACEHOLDER", db_orders_table)
                    else:
                        query = re.sub(r"db_orders_\d{2}_\d{2}_\d{4}", db_orders_table, query)
        
        # Replace hardcoded dates if query is not parameterized
        if not self.use_parameters:
            # Replace all instances of hardcoded dates in various formats
            # Replace in WHERE clauses: WHERE _source_file_date = '2025-11-07'
            query = re.sub(r"_source_file_date = '2025-11-07'", f"_source_file_date = '{old_date}'", query)
            query = re.sub(r"_source_file_date = '2025-11-10'", f"_source_file_date = '{new_date}'", query)
            # Replace in JOIN conditions: AND o._source_file_date = '2025-11-07'
            query = re.sub(r"AND o\._source_file_date = '2025-11-07'", f"AND o._source_file_date = '{old_date}'", query)
            query = re.sub(r"AND n\._source_file_date = '2025-11-10'", f"AND n._source_file_date = '{new_date}'", query)
            # Replace in SELECT AS clauses: '2025-11-07' AS old_date
            query = re.sub(r"'2025-11-07' AS old_date", f"'{old_date}' AS old_date", query)
            query = re.sub(r"'2025-11-10' AS new_date", f"'{new_date}' AS new_date", query)
            # Replace any remaining instances with quotes
            query = query.replace("'2025-11-07'", f"'{old_date}'")
            query = query.replace("'2025-11-10'", f"'{new_date}'")
        
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
        offset: int = 0,
        query_type: str = "db_comparison",
        db_orders_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute Ford field comparison query
        
        Args:
            old_date: Old date in YYYY-MM-DD format
            new_date: New date in YYYY-MM-DD format
            limit: Optional limit on number of results
            offset: Offset for pagination
            query_type: Type of query to execute
                - "db_comparison": Use ford_orders_db_comarision.sql (for DB comparison)
                - "field_comparison": Use ford_orders_field_comparison_parameterized.sql (for regular comparison)
            db_orders_date: Date for db_orders table selection (YYYY-MM-DD format)
                           Only used for db_comparison query type
                           If None, uses new_date as fallback
            
        Returns:
            Dictionary with results and metadata
        """
        # Load the appropriate query template
        self._load_query_template(query_type)
        
        # Build query and config with parameters
        query, job_config = self._build_query_config(old_date, new_date, db_orders_date)
        
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
    
    def check_db_orders_table_exists(self, date: str) -> bool:
        """
        Check if a db_orders table exists for a given date
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            True if table exists, False otherwise
        """
        from datetime import datetime as dt
        try:
            # Convert YYYY-MM-DD to MM_DD_YYYY format for table name
            date_obj = dt.strptime(date, "%Y-%m-%d")
            table_suffix = date_obj.strftime("%m_%d_%Y")
            table_name = f"db_orders_{table_suffix}"
            
            # Check if table exists
            table_ref = self.client.dataset(self.dataset_id).table(table_name)
            try:
                self.client.get_table(table_ref)
                return True
            except Exception:
                return False
        except Exception as e:
            # If any error, return False
            return False
    
    def ensure_db_orders_date_available(self, date: str) -> Dict[str, Any]:
        """
        Ensure db_orders data for a date is available in BigQuery.
        If not, automatically extract from PostgreSQL, process, and upload it.
        
        Args:
            date: Date in YYYY-MM-DD format
            
        Returns:
            Dictionary with status information
        """
        from datetime import datetime as dt
        
        # Check if table already exists
        if self.check_db_orders_table_exists(date):
            return {
                "status": "exists",
                "message": f"db_orders table for {date} already exists in BigQuery",
                "action_taken": None
            }
        
        # Convert YYYY-MM-DD to MM.DD.YYYY format for processing
        try:
            date_obj = dt.strptime(date, "%Y-%m-%d")
            process_date = date_obj.strftime("%m.%d.%Y")
        except ValueError:
            raise ValueError(f"Invalid date format: {date}. Expected YYYY-MM-DD")
        
        result = {
            "status": "processing",
            "message": f"db_orders table for {date} not found. Extracting and processing...",
            "action_taken": [],
            "date": date,
            "process_date": process_date
        }
        
        try:
            # Step 1: Extract from PostgreSQL
            result["action_taken"].append("extract")
            from data_extraction import OrdersExtractor
            extractor = OrdersExtractor()
            csv_file = extractor.export_to_csv(upload_to_gcs_flag=True)
            
            if not csv_file or not csv_file.exists():
                return {
                    "status": "error",
                    "message": f"Could not extract db_orders data for {date}",
                    "action_taken": result["action_taken"],
                    "error": "No CSV file created"
                }
            
            # Step 2: Load to BigQuery
            result["action_taken"].append("load")
            from processing.bigquery_loader import BigQueryLoader
            loader = BigQueryLoader()
            success = loader.load_orders_csv_from_local(csv_file)
            
            if not success:
                return {
                    "status": "error",
                    "message": f"Could not load db_orders data to BigQuery for {date}",
                    "action_taken": result["action_taken"],
                    "error": "BigQuery load failed"
                }
            
            # Step 3: Verify it's now in BigQuery
            import time
            time.sleep(2)
            
            if self.check_db_orders_table_exists(date):
                result["status"] = "success"
                result["message"] = f"Successfully extracted, processed, and uploaded db_orders for {date}"
                result["action_taken"].append("upload")
            else:
                result["status"] = "warning"
                result["message"] = f"Processed db_orders for {date} but may not be fully available in BigQuery yet"
            
            return result
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error processing db_orders for {date}: {str(e)}",
                "action_taken": result["action_taken"],
                "error": str(e)
            }
    
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

