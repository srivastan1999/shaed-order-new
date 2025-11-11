# 🔐 Google Cloud Credentials Setup for Vercel

## ✅ How It Works

The code automatically handles Google Cloud credentials from the `GOOGLE_APPLICATION_CREDENTIALS_JSON` environment variable.

### Pattern (Matches Node.js Example)

```python
def setup_google_credentials():
    credentials_path = '/tmp/gcp-credentials.json'
    
    # Skip if file already exists
    if os.path.exists(credentials_path):
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        return
    
    # Get JSON from environment variable
    creds_json = os.environ['GOOGLE_APPLICATION_CREDENTIALS_JSON']
    
    # Try plain JSON first, fallback to base64
    # Write to temp file for SDKs that require file path
    with open(credentials_path, 'w') as f:
        f.write(decoded_json)
    
    # Set environment variable for Google SDK
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
```

## 📋 Supported Formats

### 1. Plain JSON (Recommended)

**Easiest to use** - just copy the entire JSON file contents:

```json
{
  "type": "service_account",
  "project_id": "arcane-transit-357411",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  ...
}
```

**How to set in Vercel:**
1. Open your `.gcp-sa.json` file
2. Copy **everything** (including `{` and `}`)
3. Paste into Vercel environment variable

### 2. Base64-Encoded JSON

**Useful for** avoiding special character issues in environment variables:

```bash
# Encode to base64
cat .gcp-sa.json | base64

# Or use existing file
cat /tmp/gcp_creds_base64.txt
```

**How to set in Vercel:**
1. Get base64 string: `cat /tmp/gcp_creds_base64.txt`
2. Copy entire base64 string
3. Paste into Vercel environment variable

## 🔄 Auto-Detection

The code automatically detects which format you're using:

1. **First**: Tries to parse as plain JSON
2. **If that fails**: Tries to decode as base64, then parse JSON
3. **If both fail**: Shows clear error message

## 📁 File Location

Credentials are written to: `/tmp/gcp-credentials.json`

This matches the Node.js pattern and works in Vercel's serverless environment.

## ✅ Verification

After setting the environment variable, the health endpoint will show:

```json
{
  "status": "healthy",
  "bigquery": "connected",
  "environment": {
    "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/gcp-credentials.json",
    "GOOGLE_APPLICATION_CREDENTIALS_JSON": "SET"
  }
}
```

## 🚨 Common Issues

### Issue: "GOOGLE_APPLICATION_CREDENTIALS_JSON is neither valid JSON nor valid base64"

**Cause**: The value is malformed or incomplete.

**Fix**: 
- For plain JSON: Make sure you copied the **entire** JSON (including opening `{` and closing `}`)
- For base64: Make sure you copied the **entire** base64 string (no line breaks)

### Issue: "PROJECT_ID must be set"

**Cause**: Missing `PROJECT_ID` or `DOWNLOAD_PROJECT_ID` environment variable.

**Fix**: Set both in Vercel:
- `PROJECT_ID` = `arcane-transit-357411`
- `DOWNLOAD_PROJECT_ID` = `arcane-transit-357411`

---

**The implementation matches the Node.js pattern exactly!** ✅

