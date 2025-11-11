"""
Base OEM processor class - Common functionality for all OEM processors
"""

import glob
import os
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

import pandas as pd

from ..config import INPUT_DIR, OUTPUT_DIR
from ..utils import upload_to_gcs, get_timestamp_string, get_file_size_mb, sanitize_column_name


class BaseOEMProcessor(ABC):
    """Base class for all OEM processors"""
    
    def __init__(
        self,
        oem_name: str,
        file_pattern: str,
        input_dir: Optional[Path] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize OEM Processor
        
        Args:
            oem_name: Name of the OEM (e.g., 'Ford', 'Toyota', 'GM')
            file_pattern: File pattern to search for (e.g., "Ford Dealer Report*.xls")
            input_dir: Directory to look for Excel files. Defaults to config INPUT_DIR
            output_dir: Directory to save output files. Defaults to config OUTPUT_DIR
        """
        self.oem_name = oem_name
        self.file_pattern = file_pattern
        self.input_dir = input_dir or INPUT_DIR
        self.output_dir = output_dir or OUTPUT_DIR
        self.input_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def find_excel_files(self) -> list[Path]:
        """
        Find Excel files matching the pattern
        
        Returns:
            List of matching Excel file paths
        """
        excel_files = glob.glob(str(self.input_dir / self.file_pattern))
        return [Path(f) for f in excel_files]
    
    def get_latest_excel_file(self) -> Optional[Path]:
        """
        Get the most recent Excel file matching the pattern
        
        Returns:
            Path to the most recent file, or None if no files found
        """
        excel_files = self.find_excel_files()
        if not excel_files:
            return None
        
        # Return the most recent file
        return max(excel_files, key=os.path.getmtime)
    
    def read_excel_file(self, excel_file: Path) -> pd.DataFrame:
        """
        Read Excel file into DataFrame
        
        Args:
            excel_file: Path to Excel file
            
        Returns:
            DataFrame with data
        """
        return pd.read_excel(excel_file, dtype=str)
    
    def sanitize_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Sanitize column names for BigQuery compatibility
        
        Args:
            df: DataFrame to sanitize
            
        Returns:
            DataFrame with sanitized column names
        """
        original_columns = df.columns.tolist()
        new_columns = [sanitize_column_name(col) for col in original_columns]
        
        # Check for duplicate column names after sanitization
        duplicate_cols = [col for col in new_columns if new_columns.count(col) > 1]
        if duplicate_cols:
            print(f"⚠ Warning: Found duplicate column names after sanitization: {set(duplicate_cols)}")
            # Add suffix to duplicates
            seen = {}
            final_columns = []
            for col in new_columns:
                if col in seen:
                    seen[col] += 1
                    final_columns.append(f"{col}_{seen[col]}")
                else:
                    seen[col] = 0
                    final_columns.append(col)
            new_columns = final_columns
        
        df.columns = new_columns
        return df
    
    def clean_dataframe_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean data values (escape quotes, etc.)
        
        Args:
            df: DataFrame to clean
            
        Returns:
            Cleaned DataFrame
        """
        # Replace problematic characters in data (double quotes)
        df = df.map(lambda x: x.replace('"', '""') if isinstance(x, str) else x)
        return df
    
    @abstractmethod
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process/transform the DataFrame - OEM-specific logic
        
        This method should be implemented by each OEM processor
        to handle OEM-specific transformations.
        
        Args:
            df: DataFrame to process
            
        Returns:
            Processed DataFrame
        """
        pass
    
    def convert_excel_to_csv(
        self,
        excel_file: Optional[Path] = None,
        upload_to_gcs_flag: bool = True
    ) -> Path:
        """
        Convert Excel file to clean CSV - Main workflow
        
        Args:
            excel_file: Path to Excel file. If None, searches for files matching pattern
            upload_to_gcs_flag: Whether to upload to GCS after conversion
            
        Returns:
            Path to the created CSV file
        """
        print("=" * 60)
        print(f"{self.oem_name} Dealer Report Excel to CSV Converter")
        print("=" * 60)
        print()
        
        # Find input Excel file(s)
        if excel_file is None:
            excel_file = self.get_latest_excel_file()
            if excel_file is None:
                print(f"✗ Error: No Excel files matching pattern '{self.file_pattern}' found!")
                print(f"   Input directory: {self.input_dir}")
                sys.exit(1)
            
            excel_files = self.find_excel_files()
            if len(excel_files) > 1:
                print(f"ℹ Found {len(excel_files)} Excel files, using most recent: {excel_file.name}")
                print()
        else:
            excel_file = Path(excel_file)
        
        if not excel_file.exists():
            print(f"✗ Error: File not found: {excel_file}")
            sys.exit(1)
        
        try:
            print(f"Reading Excel file: {excel_file}")
            
            # Read Excel file
            df = self.read_excel_file(excel_file)
            
            print(f"✓ Successfully read Excel file")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            print()
            
            # Sanitize column names FIRST (before processing, so OEM processors can use sanitized names)
            print("Sanitizing column names for BigQuery compatibility...")
            df = self.sanitize_dataframe_columns(df)
            print("✓ Column names sanitized")
            print()
            
            # OEM-specific processing (after sanitization, so column names are consistent)
            print(f"Processing {self.oem_name} data...")
            df = self.process_dataframe(df)
            print(f"✓ Data processed")
            print()
            
            # Clean data values
            print("Cleaning data (replacing problematic characters)...")
            df = self.clean_dataframe_values(df)
            print("✓ Data cleaned")
            print()
            
            # Generate output filename with date from source file
            # Try to extract date from Excel filename
            date_from_file = None
            if hasattr(self, 'extract_date_from_filename'):
                print(f"ℹ Extracting date from filename: {excel_file.name}")
                date_from_file = self.extract_date_from_filename(excel_file.name)
                if date_from_file:
                    print(f"  ✓ Extracted date: {date_from_file}")
                else:
                    print(f"  ⚠ Could not extract date from filename")
            
            # Add metadata columns for BigQuery tracking
            if hasattr(self, 'add_timestamp_column') and self.add_timestamp_column:
                from datetime import datetime
                import os
                
                # Add source filename (which file this data came from)
                df['_source_filename'] = excel_file.name
                
                # Add file creation timestamp (when the source file was created)
                # Try to get from file metadata
                try:
                    # Get file creation time (ctime) or modification time (mtime) as fallback
                    file_created_time = os.path.getctime(excel_file)
                    file_created_timestamp = datetime.fromtimestamp(file_created_time).isoformat()
                except (OSError, ValueError):
                    # If can't get file time, use current time as fallback
                    file_created_timestamp = datetime.now().isoformat()
                
                df['_source_file_created_timestamp'] = file_created_timestamp
                
                # Add source file date (which date file this data came from)
                # IMPORTANT: This uses the date from the SOURCE FILE (sheet name), NOT today's date
                # This is the date extracted from the sheet filename - each order gets this date
                source_date = None
                if date_from_file:
                    # Convert YYYYMMDD to YYYY-MM-DD format for better readability
                    # date_from_file comes from extract_date_from_filename() - source file date
                    source_date = f"{date_from_file[:4]}-{date_from_file[4:6]}-{date_from_file[6:8]}"
                else:
                    # Fallback: Try to extract from filename using alternative patterns
                    import re
                    # Try different date patterns
                    patterns = [
                        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
                        r'(\d{2})/(\d{2})/(\d{4})',  # MM/DD/YYYY
                        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
                    ]
                    
                    source_date = None
                    for pattern in patterns:
                        match = re.search(pattern, excel_file.name)
                        if match:
                            if len(match.groups()) == 3:
                                if pattern == r'(\d{4})(\d{2})(\d{2})':
                                    # YYYYMMDD
                                    year, month, day = match.groups()
                                    source_date = f"{year}-{month}-{day}"
                                    break
                                elif pattern == r'(\d{2})/(\d{2})/(\d{4})':
                                    # MM/DD/YYYY
                                    month, day, year = match.groups()
                                    source_date = f"{year}-{month}-{day}"
                                    break
                                elif pattern == r'(\d{4})-(\d{2})-(\d{2})':
                                    # YYYY-MM-DD
                                    source_date = match.group(0)
                                    break
                    
                    if not source_date:
                        # Last resort: use file modification date
                        try:
                            file_date = datetime.fromtimestamp(os.path.getmtime(excel_file))
                            source_date = file_date.strftime("%Y-%m-%d")
                            print(f"⚠ Could not extract date from filename, using file modification date: {source_date}")
                        except:
                            # Final fallback: today's date (but this shouldn't happen)
                            source_date = datetime.now().strftime("%Y-%m-%d")
                            print(f"⚠ Could not extract date, using today's date: {source_date}")
                
                # Set the date for ALL rows in the dataframe
                df['_source_file_date'] = source_date  # Sheet date from filename - each order gets this
                print(f"✓ Added metadata columns:")
                print(f"  - _source_filename: {excel_file.name}")
                print(f"  - _source_file_created_timestamp: {file_created_timestamp}")
                print(f"  - _source_file_date: {source_date} (applied to all {len(df)} orders)")
                print()
            
            # Use date from filename, or fall back to today's date (no timestamp)
            if date_from_file:
                output_csv = self.output_dir / f"{self.oem_name}_Dealer_Report_clean_{date_from_file}.csv"
                print(f"ℹ Using date from source file: {date_from_file}")
            else:
                from datetime import datetime
                date_only = datetime.now().strftime("%Y%m%d")
                output_csv = self.output_dir / f"{self.oem_name}_Dealer_Report_clean_{date_only}.csv"
                print(f"ℹ Using today's date: {date_only}")
            
            # Verify metadata columns are set before saving
            if hasattr(self, 'add_timestamp_column') and self.add_timestamp_column:
                # Verify _source_file_date is set for all rows
                if '_source_file_date' in df.columns:
                    null_count = df['_source_file_date'].isna().sum()
                    if null_count > 0:
                        print(f"⚠ WARNING: {null_count} rows have NULL _source_file_date - filling with extracted date")
                        # Fill any NULL values with the extracted date
                        # source_date should already be set above, but if not, try to get it
                        if not source_date and date_from_file:
                            source_date = f"{date_from_file[:4]}-{date_from_file[4:6]}-{date_from_file[6:8]}"
                        if source_date:
                            df['_source_file_date'] = df['_source_file_date'].fillna(source_date)
                    
                    # Verify all rows have the date
                    sample_dates = df['_source_file_date'].dropna().unique()
                    if len(sample_dates) > 0:
                        print(f"  ✓ Verified: All rows have _source_file_date = '{sample_dates[0]}'")
                    else:
                        print(f"  ⚠ WARNING: No _source_file_date values found in DataFrame!")
            
            # Save as clean CSV UTF-8
            print(f"Writing to CSV file: {output_csv}")
            df.to_csv(
                output_csv,
                index=False,
                quoting=1,  # QUOTE_ALL - quote all fields
                encoding="utf-8"
            )
            
            # Show file info
            file_size_mb = get_file_size_mb(output_csv)
            
            print(f"✓ Successfully exported to CSV")
            print(f"  Output file: {output_csv}")
            print(f"  File size: {file_size_mb:.2f} MB")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {len(df.columns)}")
            
            # Final verification - check CSV has the date column
            if hasattr(self, 'add_timestamp_column') and self.add_timestamp_column:
                if '_source_file_date' in df.columns:
                    print(f"  ✓ Metadata: _source_file_date column present with {df['_source_file_date'].notna().sum()} non-null values")
            print()
            
            # Upload to GCS
            gcs_upload_success = False
            if upload_to_gcs_flag:
                print(f"Uploading to GCS bucket...")
                gcs_upload_success = upload_to_gcs(output_csv)
                print()
                
                # Load to BigQuery if this OEM supports it
                if hasattr(self, 'load_to_bigquery') and self.load_to_bigquery:
                    from ..bigquery_loader import BigQueryLoader
                    print("Loading to BigQuery...")
                    try:
                        loader = BigQueryLoader()
                        # Use OEM-specific BigQuery loading method
                        if self.oem_name.lower() == "ford":
                            # If GCS upload failed, load from local file instead
                            if not gcs_upload_success:
                                print("  ℹ GCS upload failed, loading directly from local CSV file")
                                success = loader.load_ford_oem_csv_from_local(output_csv)
                            else:
                                success = loader.load_ford_oem_csv(output_csv.name)
                        else:
                            # For other OEMs, use generic method (if needed in future)
                            success = loader.load_oem_csv(output_csv.name, self.oem_name)
                        
                        if success:
                            print("✓ BigQuery load successful")
                        else:
                            print("⚠ BigQuery load had errors (check logs above)")
                    except Exception as e:
                        print(f"⚠ BigQuery load failed: {e}")
                        import traceback
                        traceback.print_exc()
                    print()
            
            print("=" * 60)
            print("Conversion complete!")
            print("=" * 60)
            
            return output_csv
            
        except FileNotFoundError as e:
            print(f"✗ Error: File not found: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

