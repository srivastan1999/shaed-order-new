"""
Main entry point for SHAED Order ELT CLI
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_extraction import OrdersExtractor, OEMDownloader
from processing.processors import OEM_PROCESSORS


def main():
    """Main CLI entry point"""
    # Get list of available OEMs
    available_oems = list(OEM_PROCESSORS.keys())
    oems_help = f"Available OEMs: {', '.join(available_oems)}"
    
    parser = argparse.ArgumentParser(
        description="SHAED Order ELT - Extract, Load, Transform pipeline for orders and OEM dealer data"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Orders command
    orders_parser = subparsers.add_parser("orders", help="Export orders from PostgreSQL to CSV")
    orders_parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip GCS upload after export"
    )
    orders_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for CSV files (default: data/output)"
    )
    
    # OEM command - dynamic for all OEMs
    oem_parser = subparsers.add_parser(
        "oem",
        help=f"Convert OEM Excel files to CSV. {oems_help}"
    )
    oem_parser.add_argument(
        "oem_name",
        choices=available_oems,
        help=f"OEM name. {oems_help}"
    )
    oem_parser.add_argument(
        "--input-file",
        type=Path,
        help="Path to Excel file (default: searches data/input)"
    )
    oem_parser.add_argument(
        "--input-dir",
        type=Path,
        help="Input directory to search for Excel files (default: data/input)"
    )
    oem_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for CSV files (default: data/output)"
    )
    oem_parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip GCS upload after conversion"
    )
    
    # Legacy Ford command (for backward compatibility)
    ford_parser = subparsers.add_parser("ford", help="Convert Ford Excel files to CSV (legacy)")
    ford_parser.add_argument(
        "--input-file",
        type=Path,
        help="Path to Excel file (default: searches data/input)"
    )
    ford_parser.add_argument(
        "--input-dir",
        type=Path,
        help="Input directory to search for Excel files (default: data/input)"
    )
    ford_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for CSV files (default: data/output)"
    )
    ford_parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip GCS upload after conversion"
    )
    
    # Download command - Download OEM files from GCS
    download_parser = subparsers.add_parser(
        "download",
        help="Download OEM Excel files from GCS bucket"
    )
    download_parser.add_argument(
        "oem_name",
        choices=available_oems,
        help=f"OEM name. {oems_help}"
    )
    download_parser.add_argument(
        "--date",
        type=str,
        help="Single date to download (MM.DD.YYYY format, e.g., 10.29.2025)"
    )
    download_parser.add_argument(
        "--date1",
        type=str,
        help="First date (MM.DD.YYYY format)"
    )
    download_parser.add_argument(
        "--date2",
        type=str,
        help="Second date (MM.DD.YYYY format)"
    )
    download_parser.add_argument(
        "--from-env",
        action="store_true",
        help="Use dates from environment variables (DATE1, DATE2)"
    )
    download_parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for downloaded files (default: data/input)"
    )
    
    # Ford pipeline command - Download and process in one step
    ford_pipeline_parser = subparsers.add_parser(
        "ford-pipeline",
        help="Download and process Ford files in one command"
    )
    ford_pipeline_parser.add_argument(
        "--date",
        type=str,
        help="Single date to download (MM.DD.YYYY format)"
    )
    ford_pipeline_parser.add_argument(
        "--date1",
        type=str,
        help="First date (MM.DD.YYYY format)"
    )
    ford_pipeline_parser.add_argument(
        "--date2",
        type=str,
        help="Second date (MM.DD.YYYY format)"
    )
    ford_pipeline_parser.add_argument(
        "--from-env",
        action="store_true",
        help="Use dates from environment variables (DATE1, DATE2)"
    )
    ford_pipeline_parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip GCS upload after processing"
    )
    
    # All command
    all_parser = subparsers.add_parser("all", help="Run orders and all OEM processors")
    all_parser.add_argument(
        "--no-upload",
        action="store_true",
        help="Skip GCS upload after processing"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == "orders":
            extractor = OrdersExtractor(output_dir=args.output_dir)
            extractor.export_to_csv(upload_to_gcs_flag=not args.no_upload)
            
        elif args.command == "oem":
            # Dynamic OEM processor
            oem_class = OEM_PROCESSORS[args.oem_name]
            processor = oem_class(
                input_dir=args.input_dir,
                output_dir=args.output_dir
            )
            processor.convert_excel_to_csv(
                excel_file=args.input_file,
                upload_to_gcs_flag=not args.no_upload
            )
            
        elif args.command == "ford":
            # Legacy Ford command (backward compatibility)
            oem_class = OEM_PROCESSORS["ford"]
            processor = oem_class(
                input_dir=args.input_dir,
                output_dir=args.output_dir
            )
            processor.convert_excel_to_csv(
                excel_file=args.input_file,
                upload_to_gcs_flag=not args.no_upload
            )
            
        elif args.command == "download":
            # Download OEM files from GCS
            downloader = OEMDownloader(args.oem_name, output_dir=args.output_dir)
            
            # Use dates from environment variables
            if args.from_env:
                downloaded = downloader.download_from_env()
            else:
                # Collect dates from command line
                dates_to_download = []
                if args.date:
                    dates_to_download.append(args.date)
                if args.date1:
                    dates_to_download.append(args.date1)
                if args.date2:
                    dates_to_download.append(args.date2)
                
                if not dates_to_download:
                    print("ERROR: Must provide at least one date using --date, --date1, --date2, or --from-env")
                    sys.exit(1)
                
                # Download files
                downloaded = downloader.download_for_dates(dates_to_download)
            
            if downloaded:
                print(f"\n✓ Downloaded {len(downloaded)} file(s). Ready to process with:")
                print(f"  python run.py oem {args.oem_name}")
            
        elif args.command == "ford-pipeline":
            # Download and process Ford in one command
            print("=" * 60)
            print("Ford Pipeline: Download → Process → Upload")
            print("=" * 60)
            print()
            
            # Step 1: Download
            print("Step 1: Downloading Ford files from GCS...")
            print("-" * 60)
            downloader = OEMDownloader("ford")
            
            if args.from_env:
                downloaded = downloader.download_from_env()
            else:
                dates_to_download = []
                if args.date:
                    dates_to_download.append(args.date)
                if args.date1:
                    dates_to_download.append(args.date1)
                if args.date2:
                    dates_to_download.append(args.date2)
                
                if not dates_to_download:
                    print("ERROR: Must provide at least one date using --date, --date1, --date2, or --from-env")
                    sys.exit(1)
                
                downloaded = downloader.download_for_dates(dates_to_download)
            
            if not downloaded:
                print("✗ No files downloaded. Exiting.")
                sys.exit(1)
            
            print()
            print("=" * 60)
            print()
            
            # Step 2: Process all downloaded files
            print("Step 2: Processing downloaded Ford files...")
            print("-" * 60)
            processor = OEM_PROCESSORS["ford"]()
            
            # Process each downloaded file
            if downloaded:
                processed_count = 0
                for excel_file in downloaded:
                    print(f"\nProcessing: {excel_file.name}")
                    print("-" * 60)
                    try:
                        processor.convert_excel_to_csv(
                            excel_file=excel_file,
                            upload_to_gcs_flag=not args.no_upload
                        )
                        processed_count += 1
                    except Exception as e:
                        print(f"✗ Error processing {excel_file.name}: {e}")
                        continue
                
                print()
                print("=" * 60)
                print(f"✓ Ford Pipeline Complete! Processed {processed_count} file(s)")
                print("=" * 60)
            else:
                print("⚠ No files to process")
            
        elif args.command == "all":
            print("Processing orders...")
            print()
            orders_extractor = OrdersExtractor()
            orders_extractor.export_to_csv(upload_to_gcs_flag=not args.no_upload)
            
            print("\n" + "=" * 60 + "\n")
            
            # Process all OEMs
            for oem_name, oem_class in OEM_PROCESSORS.items():
                print(f"Processing {oem_name.capitalize()} reports...")
                print()
                oem_processor = oem_class()
                oem_processor.convert_excel_to_csv(upload_to_gcs_flag=not args.no_upload)
                print("\n" + "=" * 60 + "\n")
            
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

