# 🚀 What to Deploy to Vercel?

## ✅ Answer: Deploy BOTH (Frontend + Backend) from Project Root

With the configuration I've set up, you deploy **everything from the project root** in **one deployment**.

## 📦 What Gets Deployed

When you run `vercel` from the project root:

1. **Frontend** (Next.js) → Deployed as Next.js app
2. **Backend** (FastAPI) → Deployed as Python serverless function

## 🎯 How to Deploy

### Option 1: Deploy Everything (Recommended)

```bash
# From project root
cd /Users/srivastand/Desktop/vikridProjects/shaed_order_elt

# Deploy both frontend and backend
vercel --prod
```

This deploys:
- ✅ Frontend at: `https://your-app.vercel.app`
- ✅ Backend API at: `https://your-app.vercel.app/api/*`

### Option 2: Deploy Only Frontend (If Backend is Elsewhere)

If your backend is deployed separately (e.g., Google Cloud Run, Railway):

```bash
# From frontend directory
cd frontend
vercel --prod
```

Then set `NEXT_PUBLIC_API_URL` to your backend URL.

## 📁 Project Structure for Vercel

```
shaed_order_elt/              ← Deploy from HERE
├── api/
│   └── index.py             ← Backend serverless function
├── backend/                  ← Backend code (used by api/index.py)
├── frontend/                 ← Frontend Next.js app
├── vercel.json              ← Configuration (deploys both)
└── requirements.txt         ← Python dependencies
```

## 🔧 How It Works

The `vercel.json` file tells Vercel:

1. **Build Frontend**: Next.js app from `frontend/` directory
2. **Build Backend**: Python serverless function from `api/index.py`
3. **Route Requests**:
   - `/api/*` → Python serverless function (backend)
   - `/*` → Next.js frontend

## ✅ Recommended: Deploy Everything

**Deploy from project root** - this gives you:
- ✅ Frontend and backend on same domain (no CORS issues)
- ✅ Single deployment
- ✅ Easier to manage
- ✅ Better performance (same CDN)

## 🚫 Don't Deploy Separately

**Don't do this:**
- ❌ Deploy frontend separately
- ❌ Deploy backend separately
- ❌ Deploy from `frontend/` directory only

**Do this instead:**
- ✅ Deploy from project root
- ✅ One command: `vercel --prod`
- ✅ Everything works together

## 📝 Quick Deploy Command

```bash
# From project root - deploys BOTH
vercel --prod
```

That's it! Both frontend and backend will be deployed.

## 🔍 Verify Deployment

After deployment:

1. **Frontend**: `https://your-app.vercel.app`
2. **Backend Health**: `https://your-app.vercel.app/api/health`
3. **Backend API**: `https://your-app.vercel.app/api/ford-field-comparison?...`

## 💡 Summary

**Deploy from project root** → Deploys both frontend and backend together!

```bash
cd /Users/srivastand/Desktop/vikridProjects/shaed_order_elt
vercel --prod
```

