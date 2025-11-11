# ⚡ Quick Deploy to Vercel

## 🚀 Deploy in 3 Steps

### Step 1: Install & Login
```bash
npm i -g vercel
vercel login
```

### Step 2: Deploy
```bash
# From project root
vercel --prod
```

### Step 3: Add Environment Variables

Go to: **Vercel Dashboard → Project → Settings → Environment Variables**

Add:
- `NEXT_PUBLIC_API_URL` = `/api`
- `PROJECT_ID` = your GCP project ID
- `DOWNLOAD_PROJECT_ID` = your GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS_JSON` = your service account JSON

Then redeploy:
```bash
vercel --prod
```

## ✅ Done!

Your app: `https://your-app.vercel.app`

---

**Full guide:** See `DEPLOY_VERCEL.md`

