"""
BigQuery loader - Load CSV files from GCS to BigQuery tables
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from google.cloud import bigquery, storage
from google.cloud.exceptions import NotFound
from google.api_core.exceptions import BadRequest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from shared.config import GCS_BUCKET_NAME, GCS_BUCKET_PATH, DOWNLOAD_PROJECT_ID


class BigQueryLoader:
    """Load CSV files from GCS into BigQuery tables"""
    
    def __init__(self, project_id: Optional[str] = None, dataset_id: str = "shaed_elt"):
        """
        Initialize BigQuery Loader
        
        Args:
            project_id: GCP project ID (default: from env PROJECT_ID)
            dataset_id: BigQuery dataset name (default: shaed_elt)
        """
        self.project_id = project_id or DOWNLOAD_PROJECT_ID
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=self.project_id)
        self.storage_client = storage.Client(project=self.project_id)
        
        # Ensure dataset exists
        self._ensure_dataset_exists()
    
    def _ensure_dataset_exists(self):
        """Check if dataset exists, create if it doesn't"""
        dataset_ref = self.client.dataset(self.dataset_id)
        
        try:
            self.client.get_dataset(dataset_ref)
            # Dataset exists, nothing to do
        except NotFound:
            # Dataset doesn't exist, try to create it
            try:
                print(f"Creating BigQuery dataset: {self.dataset_id}")
                dataset = bigquery.Dataset(dataset_ref)
                dataset.location = "US"  # Set your preferred location
                dataset = self.client.create_dataset(dataset, exists_ok=True)
                print(f"✓ Dataset {self.dataset_id} created")
            except Exception as e:
                # If we can't create, assume it exists or will be created by admin
                # The actual load will fail with a clear error if permissions are wrong
                print(f"⚠ Note: Could not verify/create dataset {self.dataset_id}: {e}")
        except Exception as e:
            # Permission errors or other issues - continue anyway
            # The actual load operation will handle permissions properly
            print(f"⚠ Note: Could not verify dataset {self.dataset_id}: {e}")
    
    def extract_date_from_orders_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from orders CSV filename
        
        Args:
            filename: Orders CSV filename (e.g., "v_orders_api_bigquery_20251105.csv")
            
        Returns:
            Date string in MM_DD_YYYY format, or None if not found
        """
        # Pattern: YYYYMMDD in filename
        match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
        if match:
            year, month, day = match.groups()
            return f"{month}_{day}_{year}"
        return None
    
    def extract_date_from_oem_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from OEM CSV filename
        
        Args:
            filename: OEM CSV filename (e.g., "Ford_Dealer_Report_clean_20251105.csv")
            
        Returns:
            Date string in MM_DD_YYYY format, or None if not found
        """
        # Pattern: YYYYMMDD in filename
        match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
        if match:
            year, month, day = match.groups()
            return f"{month}_{day}_{year}"
        return None
    
    def load_oem_csv(self, csv_filename: str, oem_name: str) -> bool:
        """
        Load OEM CSV file to BigQuery
        
        Args:
            csv_filename: Name of CSV file (e.g., "Ford_Dealer_Report_clean_20251105.csv")
            oem_name: OEM name (e.g., "Ford", "Toyota")
            
        Returns:
            True if successful, False otherwise
        """
        # Extract date from filename
        date_str = self.extract_date_from_oem_filename(csv_filename)
        
        if not date_str:
            # Fallback: use today's date
            today = datetime.now()
            date_str = today.strftime("%m_%d_%Y")
            print(f"⚠ Could not extract date from filename, using today: {date_str}")
        
        # Create table name: db_<oem>_MM_DD_YYYY (e.g., db_ford_11_05_2025)
        oem_lower = oem_name.lower()
        table_id = f"db_{oem_lower}_{date_str}"
        
        # GCS URI
        gcs_uri = f"gs://{GCS_BUCKET_NAME}/{GCS_BUCKET_PATH}/{csv_filename}"
        
        # Load to BigQuery
        return self.load_csv_to_bigquery(gcs_uri, table_id)
    
    def _check_gcs_file_exists(self, gcs_uri: str) -> bool:
        """
        Check if a file exists in GCS
        
        Args:
            gcs_uri: GCS URI (e.g., "gs://bucket/path/file.csv")
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            # Parse GCS URI: gs://bucket/path/file.csv
            if not gcs_uri.startswith("gs://"):
                return False
            
            uri_parts = gcs_uri[5:].split("/", 1)  # Remove "gs://" and split
            if len(uri_parts) != 2:
                return False
            
            bucket_name = uri_parts[0]
            blob_name = uri_parts[1]
            
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            return blob.exists()
        except Exception as e:
            print(f"⚠ Error checking GCS file existence: {e}")
            return False
    
    def load_csv_to_bigquery(
        self,
        gcs_uri: str,
        table_id: str,
        schema: Optional[list] = None,
        write_disposition: str = "WRITE_TRUNCATE"
    ) -> bool:
        """
        Load CSV file from GCS to BigQuery table
        
        Args:
            gcs_uri: GCS URI (e.g., "gs://bucket/path/file.csv")
            table_id: BigQuery table ID
            schema: Optional schema definition
            write_disposition: WRITE_TRUNCATE (replace), WRITE_APPEND, or WRITE_EMPTY
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if file exists in GCS before attempting to load
            print(f"Checking if file exists in GCS: {gcs_uri}")
            if not self._check_gcs_file_exists(gcs_uri):
                print(f"✗ File not found in GCS: {gcs_uri}")
                print(f"  Please verify:")
                print(f"    1. The file was successfully uploaded to GCS")
                print(f"    2. The GCS path is correct")
                print(f"    3. The file name matches exactly (case-sensitive)")
                return False
            print(f"✓ File found in GCS")
            print()
            dataset_ref = self.client.dataset(self.dataset_id)
            table_ref = dataset_ref.table(table_id)
            
            # Check if table exists
            table_exists = False
            existing_table = None
            try:
                existing_table = self.client.get_table(table_ref)
                table_exists = True
                print(f"ℹ Table {table_id} already exists")
                print(f"  Current rows: {existing_table.num_rows}")
                print(f"  Current schema fields: {len(existing_table.schema)}")
            except NotFound:
                print(f"ℹ Table {table_id} does not exist, will be created")
            
            # If table exists and we're truncating, delete it first to avoid schema conflicts
            # This ensures clean replacement with auto-detected schema from CSV
            if table_exists and existing_table and write_disposition == "WRITE_TRUNCATE":
                print(f"ℹ Table exists, deleting to ensure clean replacement...")
                try:
                    self.client.delete_table(table_ref)
                    print(f"✓ Existing table deleted")
                    table_exists = False  # Reset flag since table no longer exists
                    existing_table = None
                except Exception as e:
                    print(f"⚠ Could not delete existing table: {e}")
                    print(f"  Will attempt to load with WRITE_TRUNCATE (may fail if schemas differ)")
            
            # Determine schema strategy
            if table_exists and existing_table and write_disposition == "WRITE_APPEND":
                print(f"ℹ Table exists, will append {existing_table.num_rows} existing rows")
                print(f"  ℹ Using autodetect to detect schema from new CSV data")
                print(f"  ℹ This allows new columns and better type detection")
            
            # Create job config
            if schema:
                # Use provided schema
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    schema=schema,
                    autodetect=False,
                    write_disposition=write_disposition,
                    field_delimiter=",",
                    quote_character='"',
                    allow_quoted_newlines=True,
                    encoding="UTF-8",
                    ignore_unknown_values=True,
                    max_bad_records=0,
                )
            elif table_exists and existing_table and write_disposition == "WRITE_APPEND":
                # When appending, use autodetect to let BigQuery detect schema from CSV
                # This allows new columns and better type detection from the new data
                # BigQuery will handle type conflicts by trying to cast values
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    autodetect=True,  # Autodetect schema from CSV to get new types
                    write_disposition=write_disposition,
                    field_delimiter=",",
                    quote_character='"',
                    allow_quoted_newlines=True,
                    encoding="UTF-8",
                    ignore_unknown_values=False,  # Don't ignore - we want to know about issues
                    max_bad_records=100,  # Allow some bad records for type mismatches
                )
                # Enable schema update to add new columns if present in CSV
                job_config.schema_update_options = [
                    bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
                ]
                print(f"  ℹ Schema update enabled - new columns will be added if present in CSV")
                print(f"  ⚠ Note: If column types differ, BigQuery will attempt to cast values")
                print(f"  ⚠ If casting fails, those rows will be marked as bad records")
            else:
                # Use autodetect for new tables
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    autodetect=True,  # Auto-detect schema for new tables
                    write_disposition=write_disposition,
                    field_delimiter=",",
                    quote_character='"',
                    allow_quoted_newlines=True,
                    encoding="UTF-8",
                    ignore_unknown_values=True,
                    max_bad_records=0,
                )
            
            print(f"Loading CSV to BigQuery table: {self.dataset_id}.{table_id}")
            print(f"  Source: {gcs_uri}")
            print(f"  Write disposition: {write_disposition}")
            
            # Try loading with the configured job config
            load_job = self.client.load_table_from_uri(
                gcs_uri,
                table_ref,
                job_config=job_config
            )
            
            # Wait for job to complete with timeout
            print(f"  Waiting for load job to complete...")
            try:
                load_job.result(timeout=300)  # 5 minute timeout
            except (BadRequest, Exception) as e:
                error_str = str(e).lower()
                # If autodetect failed due to type conflict when appending, try with existing schema
                if (table_exists and existing_table and 
                    write_disposition == "WRITE_APPEND" and 
                    getattr(job_config, 'autodetect', False) and
                    ("changed type" in error_str or "schema does not match" in error_str)):
                    print(f"  ⚠ Autodetect failed due to type conflict")
                    print(f"  ℹ Error: {str(e)[:200]}...")
                    print(f"  ℹ Retrying with existing table schema (will preserve existing column types)")
                    print(f"  ℹ New columns will still be added, but existing columns keep their types")
                    
                    # Retry with existing schema
                    job_config = bigquery.LoadJobConfig(
                        source_format=bigquery.SourceFormat.CSV,
                        skip_leading_rows=1,
                        schema=existing_table.schema,  # Use existing schema
                        autodetect=False,
                        write_disposition=write_disposition,
                        field_delimiter=",",
                        quote_character='"',
                        allow_quoted_newlines=True,
                        encoding="UTF-8",
                        ignore_unknown_values=True,  # Ignore CSV columns not in schema
                        max_bad_records=100,
                    )
                    job_config.schema_update_options = [
                        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
                    ]
                    
                    # Retry the load
                    load_job = self.client.load_table_from_uri(
                        gcs_uri,
                        table_ref,
                        job_config=job_config
                    )
                    print(f"  Retrying load with existing schema...")
                    load_job.result(timeout=300)
                else:
                    # Re-raise if it's a different error
                    raise
            
            # Check for errors
            if load_job.errors:
                print(f"✗ Load job completed with errors:")
                for error in load_job.errors:
                    print(f"  - {error}")
                # Check if there were bad records
                if hasattr(load_job, 'output_rows') and hasattr(load_job, 'bad_rows'):
                    if load_job.bad_rows > 0:
                        print(f"  ⚠ {load_job.bad_rows} rows were skipped due to errors")
                        print(f"  ✓ {load_job.output_rows} rows were successfully loaded")
                return False
            
            # Get updated table info
            table = self.client.get_table(table_ref)
            rows_before = existing_table.num_rows if table_exists and existing_table else 0
            rows_after = table.num_rows
            rows_added = rows_after - rows_before
            
            if write_disposition == "WRITE_APPEND":
                print(f"✓ Successfully appended {rows_added} rows to {self.dataset_id}.{table_id}")
                print(f"  Table now contains {table.num_rows} total rows (was {rows_before})")
            else:
                print(f"✓ Successfully loaded {table.num_rows} rows to {self.dataset_id}.{table_id}")
            
            print(f"  Table: {self.project_id}.{self.dataset_id}.{table_id}")
            if write_disposition == "WRITE_APPEND":
                print(f"  Data appended to existing table")
            elif table_exists and write_disposition == "WRITE_TRUNCATE":
                print(f"  Table updated (replaced existing data)")
            else:
                print(f"  Table created with {len(table.schema)} columns")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading to BigQuery: {e}")
            print(f"  GCS URI: {gcs_uri}")
            print(f"  Table: {self.project_id}.{self.dataset_id}.{table_id}")
            print()
            print("  Common causes:")
            print("    - BigQuery service account lacks permissions")
            print("    - Schema mismatch between CSV and table")
            print("    - Invalid CSV format or encoding")
            print("    - Network timeout or BigQuery quota exceeded")
            print()
            import traceback
            print("Full error details:")
            traceback.print_exc()
            return False
    
    def load_orders_csv(self, csv_filename: str) -> bool:
        """
        Load orders CSV file to BigQuery
        
        Args:
            csv_filename: Name of CSV file (e.g., "v_orders_api_bigquery_20251105.csv")
            
        Returns:
            True if successful, False otherwise
        """
        # Extract date from filename
        date_str = self.extract_date_from_orders_filename(csv_filename)
        
        if not date_str:
            # Fallback: use today's date
            today = datetime.now()
            date_str = today.strftime("%m_%d_%Y")
            print(f"⚠ Could not extract date from filename, using today: {date_str}")
        
        # Create table name: db_orders_MM_DD_YYYY
        table_id = f"db_orders_{date_str}"
        
        # GCS URI
        gcs_uri = f"gs://{GCS_BUCKET_NAME}/{GCS_BUCKET_PATH}/{csv_filename}"
        
        # Load to BigQuery
        return self.load_csv_to_bigquery(gcs_uri, table_id)
    
    def load_orders_csv_from_local(self, csv_file_path: Path) -> bool:
        """
        Load orders CSV file to BigQuery from local file (when GCS upload fails)
        
        Args:
            csv_file_path: Local path to CSV file
            
        Returns:
            True if successful, False otherwise
        """
        from pathlib import Path
        
        # Extract date from filename
        date_str = self.extract_date_from_orders_filename(csv_file_path.name)
        
        if not date_str:
            # Fallback: use today's date
            today = datetime.now()
            date_str = today.strftime("%m_%d_%Y")
            print(f"  ⚠ Could not extract date from filename, using today: {date_str}")
        
        # Create table name: db_orders_MM_DD_YYYY
        table_id = f"db_orders_{date_str}"
        
        print(f"  Loading from local file: {csv_file_path.name}")
        
        # Load directly from local file
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            table_ref = dataset_ref.table(table_id)
            
            # Check if table exists
            table_exists = False
            existing_table = None
            try:
                existing_table = self.client.get_table(table_ref)
                table_exists = True
                print(f"  ℹ Table exists, will append {existing_table.num_rows} existing rows")
            except NotFound:
                print(f"  ℹ Table does not exist, will be created")
            
            # Create job config for loading from local file
            # If table exists, build schema from CSV header that matches table schema
            # If table doesn't exist, use autodetect to create schema
            if table_exists and existing_table:
                # Read CSV header to get actual columns in the CSV
                import csv
                with open(csv_file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    csv_header = next(reader)  # Get header row
                    # Remove quotes from header if present
                    csv_header = [col.strip('"') for col in csv_header]
                
                # Build schema that matches CSV columns by name from table schema
                # This ensures we only use columns that exist in the CSV
                csv_schema = []
                table_schema_dict = {field.name: field for field in existing_table.schema}
                missing_in_table = []
                
                for col_name in csv_header:
                    if col_name in table_schema_dict:
                        # Use the existing table's field definition (including type)
                        csv_schema.append(table_schema_dict[col_name])
                    else:
                        # Column in CSV but not in table - will be added as new column
                        missing_in_table.append(col_name)
                
                if missing_in_table:
                    print(f"  ℹ CSV has {len(missing_in_table)} new columns not in table: {', '.join(missing_in_table[:5])}{'...' if len(missing_in_table) > 5 else ''}")
                
                print(f"  ℹ CSV has {len(csv_header)} columns, matched {len(csv_schema)} with table schema")
                
                # Use schema built from CSV columns (only columns that exist in CSV)
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    schema=csv_schema,  # Use schema matching only CSV columns
                    autodetect=False,  # Don't autodetect - use matched schema
                    write_disposition="WRITE_TRUNCATE",  # Orders tables are date-specific, so truncate
                    field_delimiter=",",
                    quote_character='"',
                    allow_quoted_newlines=True,
                    encoding="UTF-8",
                    ignore_unknown_values=False,  # Don't ignore - we want exact match
                    max_bad_records=100,  # Allow some bad records
                )
                print(f"  ℹ Using schema with {len(csv_schema)} fields matching CSV columns")
            else:
                # Table doesn't exist, use autodetect to create schema
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    autodetect=True,  # Auto-detect schema for new table
                    write_disposition="WRITE_TRUNCATE",  # Orders tables are date-specific
                    field_delimiter=",",
                    quote_character='"',
                    allow_quoted_newlines=True,
                    encoding="UTF-8",
                    ignore_unknown_values=True,
                    max_bad_records=0,
                )
                print(f"  ℹ Table doesn't exist, will auto-detect schema from CSV")
            
            # Load from local file
            with open(csv_file_path, 'rb') as source_file:
                load_job = self.client.load_table_from_file(
                    source_file,
                    table_ref,
                    job_config=job_config
                )
                
                print(f"  Waiting for load job to complete...")
                load_job.result(timeout=600)  # 10 minute timeout for large files
                
                if load_job.errors:
                    print(f"✗ Load job completed with errors:")
                    for error in load_job.errors:
                        print(f"  - {error}")
                    return False
                
                # Get updated table info
                table = self.client.get_table(table_ref)
                rows_before = existing_table.num_rows if table_exists and existing_table else 0
                rows_after = table.num_rows
                rows_added = rows_after - rows_before
                
                print(f"✓ Successfully loaded {rows_added} rows to {self.dataset_id}.{table_id}")
                print(f"  Table now contains {table.num_rows} total rows (was {rows_before})")
                
                return True
                
        except Exception as e:
            print(f"✗ Error loading from local file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_ford_oem_csv(self, csv_filename: str) -> bool:
        """
        Load Ford OEM CSV file to BigQuery - appends to single table
        
        All Ford files are loaded into the same table: ford_oem_orders
        Each load appends new data (does not replace existing data)
        Each order gets _source_file_date from the sheet name (filename date)
        
        NOTE: This will NOT reject duplicates. If you upload the same file twice,
        it will create duplicate rows. Use deduplication queries if needed.
        
        Args:
            csv_filename: Name of CSV file (e.g., "Ford_Dealer_Report_clean_20251105.csv")
            
        Returns:
            True if successful, False otherwise
        """
        # Fixed table name for all Ford data
        table_id = "ford_oem_orders"
        
        # GCS URI
        gcs_uri = f"gs://{GCS_BUCKET_NAME}/{GCS_BUCKET_PATH}/{csv_filename}"
        
        # Check if this exact file was already loaded (by checking for rows with same source file pattern)
        # Extract date from filename to check
        date_match = re.search(r'(\d{4})(\d{2})(\d{2})', csv_filename)
        if date_match:
            year, month, day = date_match.groups()
            date_str = f"{year}-{month}-{day}"
            
            # Check if data for this date already exists
            try:
                dataset_ref = self.client.dataset(self.dataset_id)
                table_ref = dataset_ref.table(table_id)
                
                # Query to check if data for this date exists (using _source_file_date from sheet name)
                query = f"""
                SELECT COUNT(*) as row_count
                FROM `{self.project_id}.{self.dataset_id}.{table_id}`
                WHERE _source_file_date = '{date_str}'
                """
                
                query_job = self.client.query(query)
                results = query_job.result()
                row = next(results, None)
                
                if row and row.row_count > 0:
                    print(f"⚠ Warning: Data for date {date_str} already exists in table")
                    print(f"  Found {row.row_count} existing rows for this date")
                    print(f"  This will create duplicates if the same file is loaded again")
                    print(f"  Continuing with append...")
                    print()
            except NotFound:
                # Table doesn't exist yet, first load - that's fine
                pass
            except Exception as e:
                # If check fails, continue anyway (might be permission issue)
                print(f"⚠ Could not check for existing data: {e}")
                print(f"  Continuing with load...")
        
        # Load to BigQuery with APPEND mode (adds to existing table)
        return self.load_csv_to_bigquery(
            gcs_uri, 
            table_id, 
            write_disposition="WRITE_APPEND"
        )
    
    def load_ford_oem_csv_from_local(self, csv_file_path: Path) -> bool:
        """
        Load Ford OEM CSV file to BigQuery from local file (when GCS upload fails)
        
        Args:
            csv_file_path: Local path to CSV file
            
        Returns:
            True if successful, False otherwise
        """
        from pathlib import Path
        
        table_id = "ford_oem_orders"
        
        print(f"  Loading from local file: {csv_file_path.name}")
        
        # Load directly from local file
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            table_ref = dataset_ref.table(table_id)
            
            # Check if table exists
            table_exists = False
            existing_table = None
            try:
                existing_table = self.client.get_table(table_ref)
                table_exists = True
                print(f"  ℹ Table exists, will append {existing_table.num_rows} existing rows")
            except NotFound:
                print(f"  ℹ Table does not exist, will be created")
            
            # Create job config for loading from local file
            # If table exists, build schema from CSV header that matches table schema
            # If table doesn't exist, use autodetect to create schema
            if table_exists and existing_table:
                # Read CSV header to get actual columns in the CSV
                import csv
                with open(csv_file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    csv_header = next(reader)  # Get header row
                    # Remove quotes from header if present
                    csv_header = [col.strip('"') for col in csv_header]
                
                # Build schema that matches CSV columns by name from table schema
                # This ensures we only use columns that exist in the CSV
                csv_schema = []
                table_schema_dict = {field.name: field for field in existing_table.schema}
                missing_in_table = []
                
                for col_name in csv_header:
                    if col_name in table_schema_dict:
                        # Use the existing table's field definition (including type)
                        csv_schema.append(table_schema_dict[col_name])
                    else:
                        # Column in CSV but not in table - will be added as new column
                        missing_in_table.append(col_name)
                
                if missing_in_table:
                    print(f"  ℹ CSV has {len(missing_in_table)} new columns not in table: {', '.join(missing_in_table[:5])}{'...' if len(missing_in_table) > 5 else ''}")
                
                print(f"  ℹ CSV has {len(csv_header)} columns, matched {len(csv_schema)} with table schema")
                
                # Use schema built from CSV columns (only columns that exist in CSV)
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    schema=csv_schema,  # Use schema matching only CSV columns
                    autodetect=False,  # Don't autodetect - use matched schema
                    write_disposition="WRITE_APPEND",
                    field_delimiter=",",
                    quote_character='"',
                    allow_quoted_newlines=True,
                    encoding="UTF-8",
                    ignore_unknown_values=False,  # Don't ignore - we want exact match
                    max_bad_records=100,  # Allow some bad records
                    schema_update_options=[
                        bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION
                    ],
                )
                print(f"  ℹ Using schema with {len(csv_schema)} fields matching CSV columns")
                print(f"  ℹ Schema update enabled - new columns will be added if present in CSV")
            else:
                # Table doesn't exist, use autodetect to create schema
                job_config = bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.CSV,
                    skip_leading_rows=1,
                    autodetect=True,  # Auto-detect schema for new table
                    write_disposition="WRITE_APPEND",
                    field_delimiter=",",
                    quote_character='"',
                    allow_quoted_newlines=True,
                    encoding="UTF-8",
                    ignore_unknown_values=True,
                    max_bad_records=0,
                )
                print(f"  ℹ Table doesn't exist, will auto-detect schema from CSV")
            
            # Load from local file
            with open(csv_file_path, 'rb') as source_file:
                load_job = self.client.load_table_from_file(
                    source_file,
                    table_ref,
                    job_config=job_config
                )
                
                print(f"  Waiting for load job to complete...")
                load_job.result(timeout=300)
                
                if load_job.errors:
                    print(f"✗ Load job completed with errors:")
                    for error in load_job.errors:
                        print(f"  - {error}")
                    return False
                
                # Get updated table info
                table = self.client.get_table(table_ref)
                rows_before = existing_table.num_rows if table_exists and existing_table else 0
                rows_after = table.num_rows
                rows_added = rows_after - rows_before
                
                print(f"✓ Successfully appended {rows_added} rows to {self.dataset_id}.{table_id}")
                print(f"  Table now contains {table.num_rows} total rows (was {rows_before})")
                
                return True
                
        except Exception as e:
            print(f"✗ Error loading from local file: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_table_from_query(
        self,
        query: str,
        table_id: str,
        write_disposition: str = "WRITE_TRUNCATE"
    ) -> bool:
        """
        Create a BigQuery table from a SQL query (CREATE TABLE AS SELECT)
        
        Args:
            query: SQL query to execute (should be a SELECT statement)
            table_id: Name of the table to create
            write_disposition: WRITE_TRUNCATE (replace), WRITE_APPEND, or WRITE_EMPTY
            
        Returns:
            True if successful, False otherwise
        """
        try:
            dataset_ref = self.client.dataset(self.dataset_id)
            table_ref = dataset_ref.table(table_id)
            
            # Check if table exists
            table_exists = False
            existing_table = None
            try:
                existing_table = self.client.get_table(table_ref)
                table_exists = True
                print(f"ℹ Table {table_id} already exists")
                print(f"  Current rows: {existing_table.num_rows}")
            except NotFound:
                print(f"ℹ Table {table_id} does not exist, will be created")
            
            # Build CREATE TABLE AS SELECT query
            if write_disposition == "WRITE_TRUNCATE":
                # Drop existing table if it exists
                if table_exists:
                    print(f"ℹ Dropping existing table {table_id}...")
                    self.client.delete_table(table_ref)
                    table_exists = False
                
                create_query = f"""
                CREATE OR REPLACE TABLE `{self.project_id}.{self.dataset_id}.{table_id}` AS
                {query}
                """
            elif write_disposition == "WRITE_APPEND":
                if table_exists:
                    create_query = f"""
                    INSERT INTO `{self.project_id}.{self.dataset_id}.{table_id}`
                    {query}
                    """
                else:
                    create_query = f"""
                    CREATE TABLE `{self.project_id}.{self.dataset_id}.{table_id}` AS
                    {query}
                    """
            else:  # WRITE_EMPTY
                if table_exists:
                    print(f"⚠ Table {table_id} already exists and WRITE_EMPTY specified")
                    print(f"  Skipping table creation")
                    return False
                create_query = f"""
                CREATE TABLE `{self.project_id}.{self.dataset_id}.{table_id}` AS
                {query}
                """
            
            print(f"Creating table from query: {self.dataset_id}.{table_id}")
            print(f"  Write disposition: {write_disposition}")
            
            # Execute the query
            query_job = self.client.query(create_query)
            query_job.result(timeout=300)  # 5 minute timeout
            
            # Check for errors
            if query_job.errors:
                print(f"✗ Query completed with errors:")
                for error in query_job.errors:
                    print(f"  - {error}")
                return False
            
            # Get table info
            table = self.client.get_table(table_ref)
            print(f"✓ Successfully created table {self.dataset_id}.{table_id}")
            print(f"  Table contains {table.num_rows} rows")
            print(f"  Table: {self.project_id}.{self.dataset_id}.{table_id}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error creating table from query: {e}")
            import traceback
            print("Full error details:")
            traceback.print_exc()
            return False

