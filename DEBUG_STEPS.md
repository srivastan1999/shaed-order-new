# 🔍 Debug Steps for FUNCTION_INVOCATION_FAILED

## ✅ What We've Done

1. ✅ Set all environment variables in Vercel
2. ✅ Fixed credentials handling (supports plain JSON and base64)
3. ✅ Added error handling wrapper
4. ✅ Added simple test endpoint (`/api/test`)

## 🧪 Test Endpoints

### 1. Simple Test (No BigQuery)
```bash
curl https://shaed-order-elt.vercel.app/api/test
```

**Expected**: Shows environment variable status

### 2. Health Check (Requires BigQuery)
```bash
curl https://shaed-order-elt.vercel.app/api/health
```

**Expected**: Shows health status and BigQuery connection

## 🔍 Check Vercel Logs

### Method 1: Vercel Dashboard (Best)
1. Go to: https://vercel.com/dashboard
2. Click: **shaed-order-elt** project
3. Click: **Deployments** → **Latest**
4. Click: **Functions** tab
5. Click: **View Logs**
6. Make a request: `curl https://shaed-order-elt.vercel.app/api/test`
7. **Refresh** the logs page
8. Look for:
   - Print statements from `api/index.py`
   - Error messages
   - Tracebacks

### Method 2: Command Line
```bash
# Get recent logs
vercel logs https://shaed-order-elt.vercel.app

# Or inspect specific deployment
vercel inspect https://shaed-order-elt.vercel.app --logs
```

## 📋 What to Look For

### If `/api/test` works but `/api/health` fails:
- ✅ Function is working
- ❌ BigQuery credentials or connection issue
- **Fix**: Check `GOOGLE_APPLICATION_CREDENTIALS_JSON` is set correctly

### If `/api/test` also fails:
- ❌ Function initialization issue
- **Check logs for**:
  - Import errors
  - Path issues
  - Missing dependencies

### Common Errors:

1. **"Handler not initialized"**
   - Check initialization logs
   - Look for import errors

2. **"PROJECT_ID must be set"**
   - Set `PROJECT_ID` and `DOWNLOAD_PROJECT_ID` in Vercel

3. **"Failed to initialize BigQuery service"**
   - Check `GOOGLE_APPLICATION_CREDENTIALS_JSON` is set
   - Verify credentials are valid JSON or base64

4. **"ModuleNotFoundError"**
   - Check `requirements.txt` has all dependencies
   - Redeploy

## 🚀 Next Steps

1. **Test simple endpoint**: `curl https://shaed-order-elt.vercel.app/api/test`
2. **Check logs** in Vercel Dashboard
3. **Share error message** from logs if still failing

---

**The code is correct. We need to see the actual error from Vercel logs!**

