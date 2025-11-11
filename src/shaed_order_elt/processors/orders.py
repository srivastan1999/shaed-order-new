"""
Orders processor - Export PostgreSQL orders data to CSV
"""

import csv
import sys
from pathlib import Path
from typing import Optional

import psycopg2

from ..config import (
    GCS_BUCKET_NAME,
    GCS_BUCKET_PATH,
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD,
    ORDERS_QUERY, OUTPUT_DIR
)
from ..utils import clean_value, upload_to_gcs, get_timestamp_string, get_file_size_mb
from ..bigquery_loader import BigQueryLoader


class OrdersProcessor:
    """Processor for exporting orders from PostgreSQL to CSV"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize OrdersProcessor
        
        Args:
            output_dir: Directory to save output files. Defaults to config OUTPUT_DIR
        """
        self.output_dir = output_dir or OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_to_csv(self, upload_to_gcs_flag: bool = True) -> Path:
        """
        Export PostgreSQL orders data to CSV file
        
        Args:
            upload_to_gcs_flag: Whether to upload to GCS after export
            
        Returns:
            Path to the created CSV file
        """
        print("=" * 60)
        print("PostgreSQL to CSV Export for BigQuery")
        print("=" * 60)
        print()
        
        # Generate output filename with DATE only (not time)
        # This ensures only one file per day - rerunning overwrites
        from datetime import datetime
        date_only = datetime.now().strftime("%Y%m%d")
        output_csv = self.output_dir / f"v_orders_api_bigquery_{date_only}.csv"
        
        try:
            # Connect to PostgreSQL
            print(f"Connecting to PostgreSQL: {DB_HOST}:{DB_PORT}/{DB_NAME}...")
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("✓ Connected to PostgreSQL")
            print()
            
            # Execute query
            print("Executing query...")
            print("ℹ Fetching orders from CURRENT_DATE only")
            cursor = conn.cursor()
            cursor.execute(ORDERS_QUERY)
            print("✓ Query executed successfully")
            print()
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            print(f"✓ Found {len(columns)} columns")
            print()
            
            # Fetch all rows
            print("Fetching data...")
            rows = cursor.fetchall()
            total_rows = len(rows)
            print(f"✓ Fetched {total_rows} rows")
            print()
            
            if total_rows == 0:
                print("⚠ No data to export. Exiting.")
                cursor.close()
                conn.close()
                return output_csv
            
            # Write to CSV
            print(f"Writing to CSV file: {output_csv}")
            with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
                
                # Write header
                writer.writerow(columns)
                
                # Write rows with progress
                for idx, row in enumerate(rows, 1):
                    # Clean each value
                    cleaned_row = [clean_value(val) for val in row]
                    writer.writerow(cleaned_row)
                    
                    # Show progress every 1000 rows
                    if idx % 1000 == 0:
                        print(f"  Processed {idx}/{total_rows} rows...")
            
            print(f"✓ Successfully exported {total_rows} rows to {output_csv}")
            print()
            
            # Close connections
            cursor.close()
            conn.close()
            
            # Show file info
            file_size_mb = get_file_size_mb(output_csv)
            print(f"File size: {file_size_mb:.2f} MB")
            print()
            
            # Upload to GCS
            if upload_to_gcs_flag:
                print(f"Uploading to GCS bucket...")
                upload_to_gcs(output_csv)
                print()
                
                # Load to BigQuery after successful upload
                print("Loading to BigQuery...")
                try:
                    loader = BigQueryLoader()
                    success = loader.load_orders_csv(output_csv.name)
                    if success:
                        print()
                    else:
                        print("⚠ BigQuery load failed, but CSV is available in GCS")
                        print(f"  GCS URI: gs://{GCS_BUCKET_NAME}/{GCS_BUCKET_PATH}/{output_csv.name}")
                        print("  You can:")
                        print("    1. Check the error messages above for details")
                        print("    2. Manually load the file from GCS to BigQuery")
                        print("    3. Verify BigQuery permissions and table schema")
                        print()
                except Exception as e:
                    print(f"⚠ BigQuery load error: {e}")
                    print(f"  GCS URI: gs://{GCS_BUCKET_NAME}/{GCS_BUCKET_PATH}/{output_csv.name}")
                    print("  CSV file is still available in GCS")
                    import traceback
                    print("  Full error details:")
                    traceback.print_exc()
                    print()
            
            print("=" * 60)
            print("Export complete!")
            print("=" * 60)
            
            return output_csv
            
        except psycopg2.Error as e:
            print(f"✗ PostgreSQL Error: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point for orders processor"""
    try:
        processor = OrdersProcessor()
        processor.export_to_csv()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()

