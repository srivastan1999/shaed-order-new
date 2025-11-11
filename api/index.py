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
# Supports base64-encoded JSON (matches Node.js pattern)
if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' in os.environ:
    creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON']
    try:
        import base64
        import tempfile
        
        # Decode from base64 (like Node.js: Buffer.from(..., "base64").toString("utf8"))
        decoded = base64.b64decode(creds_json).decode('utf-8')
        
        # Write to temp file (like Node.js: fs.writeFileSync(credsPath, decoded))
        # Use /tmp directory like Node.js example
        creds_path = "/tmp/gcp-creds.json"
        with open(creds_path, 'w') as f:
            f.write(decoded)
        
        # Set environment variable (like Node.js: process.env.GOOGLE_APPLICATION_CREDENTIALS = credsPath)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path
        print(f"✅ Credentials decoded from base64 and written to: {creds_path}")
        
    except base64.binascii.Error as e:
        # If base64 decode fails, try parsing as plain JSON (fallback)
        try:
            creds_data = json.loads(creds_json)
            # Write as JSON object
            import tempfile
            creds_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
            json.dump(creds_data, creds_file)
            creds_file.close()
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_file.name
            print(f"✅ Credentials parsed as plain JSON and written to: {creds_file.name}")
        except Exception as e2:
            import traceback
            print(f"❌ Error: Could not parse GOOGLE_APPLICATION_CREDENTIALS_JSON: {e2}")
            print(traceback.format_exc())
    except Exception as e:
        import traceback
        print(f"❌ Error: Could not process GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
        print(traceback.format_exc())

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

# Add a simple test to verify handler works
if __name__ == "__main__":
    # Test handler locally
    test_event = {
        "httpMethod": "GET",
        "path": "/health",
        "headers": {},
        "body": None
    }
    try:
        result = handler(test_event, {})
        print("✅ Handler test successful")
        print(f"Result: {result}")
    except Exception as e:
        print(f"❌ Handler test failed: {e}")
        import traceback
        print(traceback.format_exc())

