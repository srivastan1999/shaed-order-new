#!/usr/bin/env python3
"""
Wrapper script for SHAED Order ELT CLI
This allows running commands as: python run.py <command>
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run main
from main import main

if __name__ == "__main__":
    main()

