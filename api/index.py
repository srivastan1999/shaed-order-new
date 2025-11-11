"""
Vercel Serverless Function for FastAPI Backend
This file wraps the FastAPI app for Vercel deployment
"""
import sys
import os
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add backend to path  
backend_path = project_root / "backend"
sys.path.insert(0, str(backend_path))

# Set up environment for imports
os.chdir(project_root)

# Handle Google Cloud credentials from environment variable
if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
    creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON']
    try:
        creds_data = json.loads(creds_json)
        # Write to temp file for Google Cloud libraries
        import tempfile
        creds_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(creds_data, creds_file)
        creds_file.close()
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_file.name
    except Exception as e:
        print(f"Warning: Could not parse GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")

# Initialize handler variable
handler = None
init_error = None

try:
    print("Starting initialization...")
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Project root: {project_root}")
    print(f"Backend path exists: {backend_path.exists()}")
    
    from mangum import Mangum
    print("✅ Mangum imported")
    
    from backend.main import app
    print("✅ FastAPI app imported")
    
    # Create ASGI handler for Vercel
    handler = Mangum(app, lifespan="off")
    print("✅ FastAPI app initialized successfully")
    
except Exception as e:
    import traceback
    error_trace = traceback.format_exc()
    init_error = str(e)
    print(f"❌ Failed to initialize FastAPI app: {e}")
    print(error_trace)
    
    # Create a simple error handler
    def error_handler(request):
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Failed to initialize application',
                'message': str(e),
                'traceback': error_trace,
                'python_path': str(sys.path),
                'current_dir': os.getcwd()
            }),
            'headers': {'Content-Type': 'application/json'}
        }
    
    handler = error_handler

# Export handler for Vercel
# Vercel will call this function

