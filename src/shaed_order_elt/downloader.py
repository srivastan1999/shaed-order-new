"""
Downloader module - Download OEM files from Google Cloud Storage

Downloads Excel files from GCS bucket based on dates and OEM name.
"""

import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional

from google.cloud import storage

from .config import (
    INPUT_DIR,
    DOWNLOAD_PROJECT_ID,
    DOWNLOAD_BUCKET_NAME,
    DOWNLOAD_DATE1,
    DOWNLOAD_DATE2,
    NAME_CONTAINS
)


class GCSDownloader:
    """Download files from Google Cloud Storage"""
    
    def __init__(
        self,
        bucket_name: Optional[str] = None,
        project_id: Optional[str] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize GCS Downloader
        
        Args:
            bucket_name: GCS bucket name (default: from env BUCKET_NAME)
            project_id: GCP project ID (default: from env PROJECT_ID)
            output_dir: Output directory (default: data/input)
        """
        self.bucket_name = bucket_name or DOWNLOAD_BUCKET_NAME
        self.project_id = project_id or DOWNLOAD_PROJECT_ID
        self.output_dir = output_dir or INPUT_DIR
        
        # Validate credentials
        creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not creds or not Path(creds).exists():
            raise ValueError(
                'GOOGLE_APPLICATION_CREDENTIALS is not set or file not found.\n'
                'Set it in your environment or .env file:\n'
                'export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"'
            )
        if not self.project_id:
            raise ValueError(
                'PROJECT_ID must be set in environment variables.\n'
                'Set it in your environment or .env file:\n'
                'export PROJECT_ID="your-project-id"'
            )
        if not self.bucket_name:
            raise ValueError(
                'BUCKET_NAME must be set in environment variables.\n'
                'Set it in your environment or .env file:\n'
                'export BUCKET_NAME="your-bucket-name"'
            )
        
        # Initialize GCS client
        self.client = storage.Client(project=self.project_id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def list_files_for_date(
        self,
        date_str: str,
        name_contains: Optional[str] = None
    ) -> List[str]:
        """
        List all Excel files in the bucket for a given date
        
        Args:
            date_str: Date in MM.DD.YYYY format (e.g., "10.29.2025")
            name_contains: Substring to filter file names (optional)
            
        Returns:
            List of blob names matching the criteria
        """
        bucket = self.client.bucket(self.bucket_name)
        names: List[str] = []
        
        # Try folder-style first: Sheets/MM.DD.YYYY/*.xlsx
        prefix_folder = f'Sheets/{date_str}/'
        for blob in self.client.list_blobs(bucket, prefix=prefix_folder):
            if blob.name.lower().endswith(('.xlsx', '.xls')):
                if name_contains is None or name_contains in blob.name:
                    names.append(blob.name)
        
        # Fallback: flat naming style: Sheets_MM.DD.YYYY_*.xlsx
        if not names:
            prefix_flat = f'Sheets_{date_str}_'
            for blob in self.client.list_blobs(bucket, prefix=prefix_flat):
                if blob.name.lower().endswith(('.xlsx', '.xls')):
                    if name_contains is None or name_contains in blob.name:
                        names.append(blob.name)
        
        return names
    
    def download_file(self, blob_name: str, output_path: Optional[Path] = None) -> Path:
        """
        Download a single file from GCS
        
        Args:
            blob_name: Full path to blob in GCS
            output_path: Local path to save file (optional)
            
        Returns:
            Path to downloaded file
        """
        bucket = self.client.bucket(self.bucket_name)
        blob = bucket.blob(blob_name)
        
        # Use provided path or default to output_dir with just filename
        if output_path is None:
            local_name = Path(blob_name).name
            output_path = self.output_dir / local_name
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"  Downloading: {Path(blob_name).name}")
        blob.download_to_filename(str(output_path))
        
        # Try to preserve GCS blob creation time as file modification time
        # This helps track when the file was originally created in GCS
        try:
            # Reload blob to get metadata (time_created, etc.)
            blob.reload()
            if blob.time_created:
                import os
                # Convert GCS timestamp to local file timestamp
                blob_timestamp = blob.time_created.timestamp()
                os.utime(output_path, (blob_timestamp, blob_timestamp))
        except Exception:
            # If we can't set the timestamp, continue anyway
            pass
        
        return output_path
    
    def download_files_for_date(
        self,
        date_str: str,
        name_contains: Optional[str] = None
    ) -> List[Path]:
        """
        Download all matching files for a specific date
        
        Args:
            date_str: Date in MM.DD.YYYY format (e.g., "10.29.2025")
            name_contains: Substring to filter file names (optional)
            
        Returns:
            List of downloaded file paths
        """
        # Validate date format
        try:
            datetime.strptime(date_str, '%m.%d.%Y')
        except ValueError:
            raise ValueError(f'Invalid date format "{date_str}". Must be MM.DD.YYYY (e.g., 10.29.2025)')
        
        print(f"\nLooking for files for date: {date_str}")
        if name_contains:
            print(f"  Filtering by: {name_contains}")
        
        # List matching files
        blob_names = self.list_files_for_date(date_str, name_contains=name_contains)
        
        if not blob_names:
            print(f"  ⚠ No files found for date {date_str}")
            return []
        
        print(f"  Found {len(blob_names)} file(s)")
        
        # Download all files
        downloaded = []
        for blob_name in sorted(blob_names):
            try:
                path = self.download_file(blob_name)
                downloaded.append(path)
            except Exception as e:
                print(f"  ✗ Error downloading {blob_name}: {e}")
        
        return downloaded
    
    def download_files_for_dates(
        self,
        dates: List[str],
        name_contains: Optional[str] = None
    ) -> List[Path]:
        """
        Download files for multiple dates
        
        Args:
            dates: List of dates in MM.DD.YYYY format
            name_contains: Substring to filter file names (optional)
            
        Returns:
            List of all downloaded file paths
        """
        print(f"{'='*60}")
        print(f"Downloading files from GCS bucket: {self.bucket_name}")
        print(f"{'='*60}")
        
        all_downloaded = []
        
        for date_str in dates:
            downloaded = self.download_files_for_date(date_str, name_contains=name_contains)
            all_downloaded.extend(downloaded)
        
        # Summary
        print(f"\n{'='*60}")
        print("DOWNLOAD SUMMARY")
        print(f"{'='*60}")
        if all_downloaded:
            print(f"✓ Downloaded {len(all_downloaded)} file(s) to: {self.output_dir}")
            for f in all_downloaded:
                print(f"  • {f.name}")
        else:
            print("⚠ No files were downloaded.")
        print(f"{'='*60}\n")
        
        return all_downloaded


class OEMDownloader:
    """Download OEM-specific files from GCS"""
    
    # OEM-specific file name patterns
    OEM_PATTERNS = {
        "ford": "Ford Dealer Report",
        "toyota": "Toyota Dealer Report",
        "gm": "GM Dealer Report",
    }
    
    def __init__(self, oem_name: str, output_dir: Optional[Path] = None):
        """
        Initialize OEM Downloader
        
        Args:
            oem_name: Name of OEM (e.g., "ford", "toyota")
            output_dir: Output directory (default: data/input)
        """
        self.oem_name = oem_name.lower()
        self.downloader = GCSDownloader(output_dir=output_dir)
        
        # Get OEM-specific file pattern from env or default
        self.file_pattern = NAME_CONTAINS or self.OEM_PATTERNS.get(
            self.oem_name,
            f"{self.oem_name.capitalize()} Dealer Report"
        )
    
    def download_for_date(self, date_str: str) -> List[Path]:
        """
        Download OEM files for a specific date
        
        Args:
            date_str: Date in MM.DD.YYYY format
            
        Returns:
            List of downloaded file paths
        """
        return self.downloader.download_files_for_date(
            date_str,
            name_contains=self.file_pattern
        )
    
    def download_for_dates(self, dates: List[str]) -> List[Path]:
        """
        Download OEM files for multiple dates
        
        Args:
            dates: List of dates in MM.DD.YYYY format
            
        Returns:
            List of downloaded file paths
        """
        return self.downloader.download_files_for_dates(
            dates,
            name_contains=self.file_pattern
        )
    
    def download_from_env(self) -> List[Path]:
        """
        Download OEM files using dates from environment variables
        
        Uses DATE1 and DATE2 from .env file if set, otherwise uses today only.
        
        Returns:
            List of downloaded file paths
        """
        dates = []
        
        # Check environment variables from .env file
        if DOWNLOAD_DATE1:
            dates.append(DOWNLOAD_DATE1)
            print(f"ℹ Using DATE1 from .env: {DOWNLOAD_DATE1}")
        if DOWNLOAD_DATE2:
            dates.append(DOWNLOAD_DATE2)
            print(f"ℹ Using DATE2 from .env: {DOWNLOAD_DATE2}")
        
        # If no dates in env, use today only
        if not dates:
            today = datetime.now()
            today_str = today.strftime('%m.%d.%Y')
            dates = [today_str]
            print(f"ℹ No DATE1/DATE2 in .env, using today: {today_str}")
        
        return self.download_for_dates(dates)
