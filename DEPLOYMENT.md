# Deployment Guide

This guide covers deploying the SHAED Order ELT application to production.

## Architecture

- **Frontend**: Next.js app deployed on Vercel
- **Backend**: FastAPI app (can be deployed on Cloud Run, Railway, or similar)
- **Database**: BigQuery (Google Cloud)
- **Storage**: Google Cloud Storage

## Frontend Deployment (Vercel)

### Prerequisites

1. Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. Backend API deployed and accessible

### Step 1: Prepare Frontend

```bash
cd frontend
npm install
```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
cd frontend
vercel login
vercel
```

Follow the prompts:
- Set up and deploy? **Yes**
- Which scope? (Select your account/team)
- Link to existing project? **No** (first time) or **Yes** (updates)
- What's your project's name? `shaed-order-elt-frontend`
- In which directory is your code located? `./`
- Want to override settings? **No**

#### Option B: Using Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your project (upload or connect via CLI)
3. Configure:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `.next`
4. Add Environment Variables:
   - `NEXT_PUBLIC_API_URL`: Your backend API URL (e.g., `https://api.yourdomain.com`)

### Step 3: Configure Environment Variables

In Vercel Dashboard → Your Project → Settings → Environment Variables:

```
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

### Step 4: Deploy

If using CLI:
```bash
vercel --prod
```

If using Dashboard, redeploy from the Vercel dashboard.

## Backend Deployment Options

### Option 1: Google Cloud Run (Recommended)

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/shaed-order-elt-backend
gcloud run deploy shaed-order-elt-backend \
  --image gcr.io/YOUR_PROJECT_ID/shaed-order-elt-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=YOUR_PROJECT_ID"
```

### Option 2: Railway

1. Go to https://railway.app
2. New Project → Deploy from local directory or upload
3. Add environment variables in Railway dashboard
4. Deploy

### Option 3: Render

1. Go to https://render.com
2. New Web Service
3. Upload your project or connect via CLI
4. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

## Environment Variables

### Frontend (Vercel)

- `NEXT_PUBLIC_API_URL`: Backend API URL

### Backend

- `PROJECT_ID`: Google Cloud Project ID
- `GCS_BUCKET_NAME`: Google Cloud Storage bucket name
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: PostgreSQL credentials
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to GCP service account JSON (or use default credentials)

## CORS Configuration

Update `backend/main.py` to allow your Vercel domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",
        "http://localhost:3000",  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Post-Deployment Checklist

- [ ] Frontend deployed to Vercel
- [ ] Backend deployed and accessible
- [ ] Environment variables configured
- [ ] CORS configured for Vercel domain
- [ ] Health check endpoint working
- [ ] API endpoints accessible from frontend
- [ ] BigQuery credentials configured
- [ ] GCS bucket accessible

## Monitoring

### Vercel Analytics

Enable in Vercel Dashboard → Analytics

### Backend Logs

- **Cloud Run**: View logs in Google Cloud Console
- **Railway**: View logs in Railway dashboard
- **Render**: View logs in Render dashboard

## Custom Domain

### Vercel

1. Go to Project Settings → Domains
2. Add your domain
3. Configure DNS as instructed

### Backend

Update CORS to include your custom domain.

## Troubleshooting

### Frontend can't connect to backend

1. Check `NEXT_PUBLIC_API_URL` is set correctly
2. Verify backend is accessible (test with curl)
3. Check CORS configuration
4. Verify backend health endpoint: `curl https://your-backend.com/health`

### Build errors

1. Check Node.js version (Vercel uses Node 18+)
2. Verify all dependencies in `package.json`
3. Check build logs in Vercel dashboard

### API errors

1. Check backend logs
2. Verify BigQuery credentials
3. Check GCS bucket permissions
4. Verify environment variables

## Continuous Deployment

Vercel can be configured for automatic deployments when using their CLI or dashboard.

## Security

- Never commit `.env` files
- Use Vercel environment variables
- Enable Vercel's DDoS protection
- Use HTTPS (automatic with Vercel)
- Secure backend API (add authentication if needed)

