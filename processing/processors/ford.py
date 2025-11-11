"""
Ford processor - Convert Ford Dealer Report Excel files to CSV
Ford-specific logic can be added in process_dataframe() method
"""

import re
from pathlib import Path
from typing import Optional

import pandas as pd

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from shared.config import FORD_EXCEL_PATTERN
from .base_oem import BaseOEMProcessor


class FordProcessor(BaseOEMProcessor):
    """Processor for converting Ford Dealer Report Excel files to CSV"""
    
    def __init__(self, input_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        """
        Initialize FordProcessor
        
        Args:
            input_dir: Directory to look for Excel files. Defaults to config INPUT_DIR
            output_dir: Directory to save output files. Defaults to config OUTPUT_DIR
        """
        super().__init__(
            oem_name="Ford",
            file_pattern=FORD_EXCEL_PATTERN,
            input_dir=input_dir,
            output_dir=output_dir
        )
        # Enable timestamp column for BigQuery tracking
        self.add_timestamp_column = True
        # Enable BigQuery loading
        self.load_to_bigquery = True
    
    def extract_date_from_filename(self, filename: str) -> Optional[str]:
        """
        Extract date from Ford filename
        
        Args:
            filename: Ford Excel filename (e.g., "Ford Dealer Report-11.03.2025.xlsx")
            
        Returns:
            Date string in YYYYMMDD format, or None if not found
        """
        # Pattern: MM.DD.YYYY in filename
        match = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', filename)
        if match:
            month, day, year = match.groups()
            return f"{year}{month}{day}"
        return None
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process Ford-specific data transformations
        
        Add any Ford-specific logic here:
        - Remove specific rows/columns
        - Transform data formats
        - Add calculated fields
        - etc.
        
        Args:
            df: Raw DataFrame from Excel
            
        Returns:
            Processed DataFrame
        """
        # Convert date columns from MM/DD/YYYY to YYYY-MM-DD format for BigQuery compatibility
        # List of date column names that should be converted
        date_columns = [
            'Last_Updated', 'Status_Last_Updated', 'Last_Location_Date',
            'Order_Received', 'Scheduled_Date', 'Last_Updated_Estimated_Build_Date',
            'Estimated_Build_Date', 'Plant_Date', 'Produced_Date', 'Released_Date',
            'Shipped_Date', 'Ship_Through_Received_Date', 'Ship_Through_Started_Date',
            'Ship_Through_Completed_Date', 'Delivered_Date', 'Upfitter_Estimated_Start_Date',
            'Upfitter_Estimated_Completion_Date', 'Post_Delivered_Upfitting_Last_Updated'
        ]
        
        from datetime import datetime
        
        for col in date_columns:
            if col in df.columns:
                def convert_date(value):
                    if pd.isna(value) or value == '' or value is None:
                        return None
                    value_str = str(value).strip()
                    if not value_str:
                        return None
                    # Try to parse MM/DD/YYYY format
                    try:
                        # Try MM/DD/YYYY format
                        date_obj = datetime.strptime(value_str, '%m/%d/%Y')
                        return date_obj.strftime('%Y-%m-%d')
                    except ValueError:
                        try:
                            # Try YYYY-MM-DD format (already correct)
                            date_obj = datetime.strptime(value_str, '%Y-%m-%d')
                            return value_str  # Already in correct format
                        except ValueError:
                            # If can't parse, return as-is (will be NULL in BigQuery)
                            return None
                
                # Convert the column
                df[col] = df[col].apply(convert_date)
        
        return df


def main():
    """Main entry point for Ford processor"""
    try:
        processor = FordProcessor()
        processor.convert_excel_to_csv()
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    main()

