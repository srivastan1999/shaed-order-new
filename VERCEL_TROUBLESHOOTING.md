# 🔧 Vercel Deployment Troubleshooting

## Error: 500 INTERNAL_SERVER_ERROR - FUNCTION_INVOCATION_FAILED

This error means the serverless function failed to execute. Here's how to fix it:

### 1. Check Function Logs

Go to **Vercel Dashboard → Your Project → Functions → View Logs**

Look for:
- Import errors
- Missing dependencies
- Credential errors
- Path issues

### 2. Common Issues & Fixes

#### Issue: Import Errors

**Error**: `ModuleNotFoundError: No module named 'backend'`

**Fix**: The path setup in `api/index.py` should handle this. Make sure:
- `api/index.py` exists
- Project structure is correct
- All files are committed to Git

#### Issue: Missing Dependencies

**Error**: `ModuleNotFoundError: No module named 'mangum'`

**Fix**: Add to `requirements.txt`:
```
mangum>=0.17.0
```

Then redeploy.

#### Issue: BigQuery Credentials

**Error**: `Failed to initialize BigQuery service`

**Fix**: Set environment variable in Vercel:
- Key: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- Value: Your entire service account JSON (paste the whole JSON)

#### Issue: Environment Variables Not Set

**Error**: `PROJECT_ID not set`

**Fix**: Add these environment variables in Vercel:
- `PROJECT_ID` = your GCP project ID
- `DOWNLOAD_PROJECT_ID` = your GCP project ID
- `ENVIRONMENT` = `production`

### 3. Test Locally First

Before deploying, test the handler locally:

```bash
# Install dependencies
pip install mangum

# Test import
python3 -c "import sys; sys.path.insert(0, '.'); from api.index import handler; print('OK')"
```

### 4. Check Vercel Configuration

Make sure `vercel.json` is correct:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/next"
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ]
}
```

### 5. Verify File Structure

```
shaed_order_elt/
├── api/
│   └── index.py          ✅ Must exist
├── backend/
│   ├── main.py
│   └── services/
├── frontend/
│   └── package.json
├── vercel.json           ✅ Must exist
└── requirements.txt      ✅ Must include mangum
```

### 6. Debug Steps

1. **Check Logs**: Vercel Dashboard → Functions → Logs
2. **Test Health Endpoint**: `curl https://your-app.vercel.app/api/health`
3. **Check Environment Variables**: Vercel Dashboard → Settings → Environment Variables
4. **Verify Dependencies**: Check `requirements.txt` has all packages

### 7. Quick Fixes

#### Fix 1: Add Missing Dependency
```bash
# Add to requirements.txt
echo "mangum>=0.17.0" >> requirements.txt
```

#### Fix 2: Update Handler
Make sure `api/index.py` exports `handler` correctly.

#### Fix 3: Set Credentials
In Vercel Dashboard → Environment Variables:
- Add `GOOGLE_APPLICATION_CREDENTIALS_JSON` with your service account JSON

### 8. Still Not Working?

1. Check Vercel Function Logs for exact error
2. Test locally: `python3 api/index.py`
3. Verify all environment variables are set
4. Make sure `requirements.txt` includes all dependencies
5. Check that `vercel.json` routes are correct

### 9. Get Help

Share:
- Error message from Vercel logs
- Your `vercel.json` content
- Your `api/index.py` content
- Environment variables (without sensitive data)

