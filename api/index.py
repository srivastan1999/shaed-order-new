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

def setup_google_credentials():
    """
    Setup Google Cloud credentials from environment variable.
    Matches Node.js pattern: write JSON to temp file for SDKs that require file path.
    
    Supports:
    - Plain JSON string (most common)
    - Base64-encoded JSON (for easier storage in env vars)
    """
    credentials_path = '/tmp/gcp-credentials.json'
    
    # Only setup if GOOGLE_APPLICATION_CREDENTIALS_JSON is set
    if 'GOOGLE_APPLICATION_CREDENTIALS_JSON' not in os.environ:
        return
    
    # Skip if file already exists (like Node.js example)
    if os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        print(f"✅ Using existing credentials file: {credentials_path}")
        return
    
    creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON']
    
    try:
        # Try parsing as plain JSON first (most common case)
        try:
            # Validate it's valid JSON
            creds_data = json.loads(creds_json)
            # Write JSON to temp file (like Node.js: fs.writeFileSync(credsPath, decoded))
            with open(credentials_path, 'w') as f:
                json.dump(creds_data, f)
            print(f"✅ Credentials parsed as JSON and written to: {credentials_path}")
        except json.JSONDecodeError:
            # If JSON parsing fails, try base64 decode (like Node.js: Buffer.from(..., "base64").toString("utf8"))
            import base64
            try:
                decoded = base64.b64decode(creds_json).decode('utf-8')
                # Validate decoded string is JSON
                json.loads(decoded)  # Validate
                # Write decoded JSON to temp file
                with open(credentials_path, 'w') as f:
                    f.write(decoded)
                print(f"✅ Credentials decoded from base64 and written to: {credentials_path}")
            except (base64.binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
                raise ValueError(f"GOOGLE_APPLICATION_CREDENTIALS_JSON is neither valid JSON nor valid base64-encoded JSON: {e}")
        
        # Set environment variable (like Node.js: process.env.GOOGLE_APPLICATION_CREDENTIALS = credsPath)
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Error: Could not process GOOGLE_APPLICATION_CREDENTIALS_JSON: {e}")
        print(error_trace)
        # Don't raise - let the app start and fail gracefully when BigQuery is used
        # This allows health check to show what's wrong

# Setup Google Cloud credentials before importing FastAPI app
setup_google_credentials()

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
    def error_handler(event, context):
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

# Create a safe wrapper function for Vercel
# This ensures we always return proper error responses
def safe_handler(event, context):
    """
    Safe wrapper for Vercel Python function handler.
    Catches any errors and returns them in a proper format.
    """
    try:
        if handler is None:
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Handler not initialized',
                    'init_error': str(init_error) if init_error else 'Unknown error'
                }),
                'headers': {'Content-Type': 'application/json'}
            }
        # Call the handler (Mangum instance or error handler)
        return handler(event, context)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"❌ Handler execution error: {e}")
        print(error_trace)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Handler execution failed',
                'message': str(e),
                'traceback': error_trace
            }),
            'headers': {'Content-Type': 'application/json'}
        }

# Export handler for Vercel
# Vercel Python expects a callable named 'handler'
# If handler is None or not properly initialized, use safe_handler
# Otherwise, Mangum instance is callable and will work directly
if handler is None:
    handler = safe_handler
else:
    # Wrap the handler to catch runtime errors
    original_handler = handler
    def handler(event, context):
        try:
            return original_handler(event, context)
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"❌ Handler execution error: {e}")
            print(error_trace)
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': 'Handler execution failed',
                    'message': str(e),
                    'traceback': error_trace
                }),
                'headers': {'Content-Type': 'application/json'}
            }

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

