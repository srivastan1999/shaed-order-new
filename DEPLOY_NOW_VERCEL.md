# 🚀 Deploy to Vercel NOW - Quick Guide

## ⚡ One-Command Deploy

```bash
# From project root
vercel login && vercel --prod
```

## 📋 Step-by-Step

### 1. Install Vercel CLI (if not installed)
```bash
npm i -g vercel
```

### 2. Login
```bash
vercel login
```

### 3. Deploy
```bash
# From project root directory
cd /Users/srivastand/Desktop/vikridProjects/shaed_order_elt

# Deploy (first time - preview)
vercel

# Follow prompts:
# - Set up and deploy? → Yes
# - Which scope? → Your account
# - Link to existing project? → No
# - Project name? → shaed-order-elt
# - Directory? → ./
# - Override settings? → No

# Deploy to production
vercel --prod
```

### 4. Set Environment Variables

After deployment, go to: **Vercel Dashboard → Your Project → Settings → Environment Variables**

Add these:

```
NEXT_PUBLIC_API_URL=/api
PROJECT_ID=your-gcp-project-id
DOWNLOAD_PROJECT_ID=your-gcp-project-id
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app.vercel.app
```

For Google Cloud credentials, add:
```
GOOGLE_APPLICATION_CREDENTIALS_JSON={"type":"service_account",...}
```
(Paste your entire service account JSON)

### 5. Redeploy
```bash
vercel --prod
```

## ✅ That's It!

Your app will be live at: `https://your-app.vercel.app`

## 🔍 Test It

```bash
# Health check
curl https://your-app.vercel.app/api/health

# Test API
curl "https://your-app.vercel.app/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10&limit=10"
```

## 📚 Full Guide

See `DEPLOY_VERCEL.md` for detailed instructions.

