# 🚨 FIX FUNCTION_INVOCATION_FAILED - Step by Step

## Problem
The function is crashing because **environment variables are NOT set in Vercel**.

## ✅ Solution (5 minutes)

### Step 1: Get Your Base64 Credentials

```bash
cat /tmp/gcp_creds_base64.txt
```

**Copy the entire output** (it's a long base64 string)

### Step 2: Go to Vercel Dashboard

1. Open: **https://vercel.com/dashboard**
2. Click: **Your Project** (`shaed-order-elt`)
3. Click: **Settings** (top menu)
4. Click: **Environment Variables** (left sidebar)

### Step 3: Add These 5 Variables

#### Variable 1: GOOGLE_APPLICATION_CREDENTIALS_JSON
- **Key**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- **Value**: 
  - **Option A (Plain JSON - Recommended)**: Copy entire contents of `.gcp-sa.json` file
  - **Option B (Base64)**: Paste the base64 string from Step 1
- **Note**: Code auto-detects plain JSON or base64
- **Environments**: ✅ Production ✅ Preview ✅ Development

#### Variable 2: PROJECT_ID
- **Key**: `PROJECT_ID`
- **Value**: `arcane-transit-357411`
- **Environments**: ✅ All

#### Variable 3: DOWNLOAD_PROJECT_ID
- **Key**: `DOWNLOAD_PROJECT_ID`
- **Value**: `arcane-transit-357411`
- **Environments**: ✅ All

#### Variable 4: ENVIRONMENT
- **Key**: `ENVIRONMENT`
- **Value**: `production`
- **Environments**: ✅ All

#### Variable 5: NEXT_PUBLIC_API_URL
- **Key**: `NEXT_PUBLIC_API_URL`
- **Value**: `/api`
- **Environments**: ✅ All

### Step 4: Redeploy

After adding variables, Vercel will ask: **"Redeploy all deployments?"**

Click: **✅ Redeploy**

OR run:
```bash
vercel --prod
```

### Step 5: Test (Wait 30 seconds after deploy)

```bash
curl https://shaed-order-elt.vercel.app/api/health
```

## ✅ Expected Response

```json
{
  "status": "healthy",
  "bigquery": "connected",
  "environment": {
    "PROJECT_ID": "arcane-transit-357411",
    "DOWNLOAD_PROJECT_ID": "arcane-transit-357411",
    "GOOGLE_APPLICATION_CREDENTIALS": "/tmp/gcp-creds.json",
    "GOOGLE_APPLICATION_CREDENTIALS_JSON": "SET"
  }
}
```

## ❌ If Still Failing

The health endpoint will now show **which variables are missing**:

```json
{
  "status": "unhealthy",
  "error": "...",
  "environment": {
    "PROJECT_ID": "NOT SET",  ← This shows what's missing!
    ...
  }
}
```

## 📊 Check Logs

If still failing, check logs:
1. Vercel Dashboard → **Deployments** → **Latest**
2. Click **Functions** tab
3. Click **View Logs**
4. Make a request: `curl https://shaed-order-elt.vercel.app/api/health`
5. **Refresh** logs page

---

**The code is correct. You just need to set the environment variables!**

