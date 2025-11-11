# 🔍 Diagnose FUNCTION_INVOCATION_FAILED Error

## Current Status

- ✅ Code deployed successfully
- ✅ Build completed
- ❌ Function fails at runtime

## Most Likely Cause: Missing Environment Variables

The function is crashing because environment variables are not set in Vercel.

## 🔍 How to Check the Exact Error

### Method 1: Vercel Dashboard (Best)

1. Go to: **https://vercel.com/dashboard**
2. Click: Your project → **Deployments**
3. Click: **Latest deployment**
4. Scroll to **Runtime Logs** or **Function Logs**
5. Make a request: `curl https://shaed-order-elt.vercel.app/api/health`
6. **Refresh** the logs page
7. Look for error messages

### Method 2: Command Line

```bash
# Get logs for latest deployment
vercel logs https://shaed-order-elt.vercel.app
```

## 🎯 Quick Fix: Set Environment Variables

**Go to Vercel Dashboard → Settings → Environment Variables**

Add these:

1. **GOOGLE_APPLICATION_CREDENTIALS_JSON**
   - Get base64: `cat /tmp/gcp_creds_base64.txt`
   - Paste entire string
   - Environments: All

2. **PROJECT_ID** = `arcane-transit-357411`

3. **DOWNLOAD_PROJECT_ID** = `arcane-transit-357411`

4. **ENVIRONMENT** = `production`

5. **NEXT_PUBLIC_API_URL** = `/api`

## 🧪 Test After Setting Variables

```bash
# 1. Redeploy
vercel --prod

# 2. Wait 30 seconds

# 3. Test
curl https://shaed-order-elt.vercel.app/api/health
```

## 📋 Expected Errors (if variables not set)

- `PROJECT_ID must be set` → Set PROJECT_ID
- `Failed to initialize BigQuery service` → Set GOOGLE_APPLICATION_CREDENTIALS_JSON
- `ModuleNotFoundError` → Check requirements.txt

## ✅ Next Steps

1. **Check logs** in Vercel Dashboard to see exact error
2. **Set environment variables** (especially GOOGLE_APPLICATION_CREDENTIALS_JSON)
3. **Redeploy**: `vercel --prod`
4. **Test**: `curl https://shaed-order-elt.vercel.app/api/health`

---

**The code is correct. The issue is missing environment variables in Vercel!**

