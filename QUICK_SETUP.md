# ⚡ Quick Setup - Deploy & Test

## ✅ Step 1: Set Environment Variables in Vercel

**IMPORTANT**: Do this FIRST before deploying!

1. Go to: **https://vercel.com/dashboard**
2. Click: Your project → **Settings** → **Environment Variables**
3. Add these variables:

### Variable 1: GOOGLE_APPLICATION_CREDENTIALS_JSON

**Key**: `GOOGLE_APPLICATION_CREDENTIALS_JSON`

**Value**: (The base64 string is saved in `/tmp/gcp_creds_base64.txt` on your machine)

To get it, run:
```bash
cat /tmp/gcp_creds_base64.txt
```

**Copy the ENTIRE output** (it's a long string starting with `ewogICJ0eXBlIjogInNlcnZpY2VfYWNjb3VudCIs...`)

**Environments**: ✅ Production, ✅ Preview, ✅ Development

### Variable 2: PROJECT_ID

**Key**: `PROJECT_ID`  
**Value**: `arcane-transit-357411`  
**Environments**: ✅ All

### Variable 3: DOWNLOAD_PROJECT_ID

**Key**: `DOWNLOAD_PROJECT_ID`  
**Value**: `arcane-transit-357411`  
**Environments**: ✅ All

### Variable 4: ENVIRONMENT

**Key**: `ENVIRONMENT`  
**Value**: `production`  
**Environments**: ✅ All

### Variable 5: NEXT_PUBLIC_API_URL

**Key**: `NEXT_PUBLIC_API_URL`  
**Value**: `/api`  
**Environments**: ✅ All

## 🚀 Step 2: Deploy

After setting variables, run:

```bash
vercel --prod
```

## 🧪 Step 3: Test

```bash
# Test health
curl https://shaed-order-elt.vercel.app/api/health

# Test API
curl "https://shaed-order-elt.vercel.app/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10&limit=5"
```

## 📋 Or Use the Script

```bash
./DEPLOY_AND_TEST.sh
```

---

**⚠️ CRITICAL**: Set environment variables in Vercel Dashboard FIRST, then deploy!

