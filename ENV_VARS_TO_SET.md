# 🔐 Environment Variables to Set in Vercel

## ⚠️ CRITICAL: Set These BEFORE Testing!

Go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

## 📋 Variables to Add:

### 1. GOOGLE_APPLICATION_CREDENTIALS_JSON

**Key**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`

**Value**: You can use **either**:
- **Plain JSON** (recommended): Copy entire contents of `.gcp-sa.json` file
- **Base64-encoded JSON**: Get it by running:
  ```bash
  cat /tmp/gcp_creds_base64.txt
  ```
  Copy the ENTIRE output (long base64 string)

**Note**: The code automatically detects if it's plain JSON or base64-encoded.

**Environments**: ✅ Production, ✅ Preview, ✅ Development

### 2. PROJECT_ID

**Key**: `PROJECT_ID`  
**Value**: `arcane-transit-357411`  
**Environments**: ✅ All

### 3. DOWNLOAD_PROJECT_ID

**Key**: `DOWNLOAD_PROJECT_ID`  
**Value**: `arcane-transit-357411`  
**Environments**: ✅ All

### 4. ENVIRONMENT

**Key**: `ENVIRONMENT`  
**Value**: `production`  
**Environments**: ✅ All

### 5. NEXT_PUBLIC_API_URL

**Key**: `NEXT_PUBLIC_API_URL`  
**Value**: `/api`  
**Environments**: ✅ All

## 🚀 After Setting Variables:

1. **Redeploy** (or wait for auto-deploy):
   ```bash
   vercel --prod
   ```

2. **Test**:
   ```bash
   curl https://shaed-order-elt.vercel.app/api/health
   ```

## ✅ Expected Response:

```json
{"status":"healthy","bigquery":"connected"}
```

---

**The base64 credentials are ready in `/tmp/gcp_creds_base64.txt`**

