# 🚀 Complete Vercel Deployment Guide

This guide will help you deploy **both frontend and backend** to Vercel in one go!

## 📋 Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com (free)
2. **Vercel CLI**: Install globally
   ```bash
   npm i -g vercel
   ```
3. **Git Repository**: Your code should be in a Git repo (GitHub, GitLab, or Bitbucket)

## 🎯 Quick Deploy (5 Minutes)

### Step 1: Install Dependencies

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Install Python dependencies (for serverless functions)
pip install mangum
```

### Step 2: Login to Vercel

```bash
vercel login
```

### Step 3: Deploy Everything

From the project root:

```bash
# Deploy to Vercel (preview)
vercel

# Follow prompts:
# - Set up and deploy? → Yes
# - Which scope? → Your account
# - Link to existing project? → No (first time)
# - What's your project's name? → shaed-order-elt
# - In which directory is your code located? → ./
# - Want to override settings? → No

# After successful preview, deploy to production:
vercel --prod
```

### Step 4: Configure Environment Variables

After deployment, go to Vercel Dashboard:

1. Go to your project → **Settings** → **Environment Variables**
2. Add these variables:

#### Frontend Variables:
```
NEXT_PUBLIC_API_URL=/api
```

#### Backend Variables:
```
PROJECT_ID=your-gcp-project-id
DOWNLOAD_PROJECT_ID=your-gcp-project-id
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

#### Google Cloud Credentials:
For BigQuery and GCS access, you have two options:

**Option A: Service Account Key (Recommended)**
1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. In Vercel Dashboard → Settings → Environment Variables:
   - Key: `GOOGLE_APPLICATION_CREDENTIALS_JSON`
   - Value: Paste the entire JSON content
   - Environment: Production, Preview, Development

**Option B: Default Credentials**
- If running on Google Cloud, use default credentials
- Set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account JSON

### Step 5: Redeploy

After adding environment variables:

```bash
vercel --prod
```

Or redeploy from Vercel Dashboard.

## 📁 Project Structure for Vercel

```
shaed_order_elt/
├── api/
│   └── index.py          # Serverless function entry point
├── frontend/             # Next.js frontend
│   ├── app/
│   ├── components/
│   └── package.json
├── backend/               # FastAPI backend (used by serverless function)
│   ├── main.py
│   └── services/
├── vercel.json           # Vercel configuration
└── requirements.txt      # Python dependencies
```

## 🔧 Configuration Files

### vercel.json
This file configures:
- Frontend build (Next.js)
- Backend serverless function
- Routing rules

### api/index.py
This is the serverless function that:
- Wraps your FastAPI app
- Handles all `/api/*` requests
- Uses Mangum to convert ASGI to serverless format

## 🌐 How It Works

1. **Frontend** (`/`): Served by Next.js on Vercel
2. **Backend API** (`/api/*`): Handled by Python serverless function
3. **Routing**: 
   - `/api/*` → Python serverless function
   - `/*` → Next.js frontend

## 🔍 Testing Deployment

### 1. Test Frontend
Visit: `https://your-app.vercel.app`

### 2. Test Backend Health
```bash
curl https://your-app.vercel.app/api/health
```

### 3. Test API Endpoint
```bash
curl "https://your-app.vercel.app/api/ford-field-comparison?old_date=2025-11-07&new_date=2025-11-10&limit=10"
```

## 🐛 Troubleshooting

### Build Fails

**Error: Module not found**
- Check `requirements.txt` includes all dependencies
- Ensure `mangum` is installed

**Error: Python version**
- Vercel uses Python 3.11 by default
- Check your code is compatible

### API Not Working

**Error: 500 Internal Server Error**
- Check Vercel Function Logs (Dashboard → Functions → View Logs)
- Verify environment variables are set
- Check BigQuery credentials

**Error: CORS**
- Update `ALLOWED_ORIGINS` with your Vercel URL
- Include both production and preview URLs

### Frontend Can't Connect to Backend

**Error: Network Error**
- Check `NEXT_PUBLIC_API_URL` is set to `/api` (relative URL)
- Verify backend is deployed and working
- Check browser console for errors

## 📊 Monitoring

### Vercel Dashboard
- **Deployments**: View all deployments
- **Functions**: Monitor serverless function performance
- **Analytics**: View traffic and performance metrics
- **Logs**: Real-time function logs

### Function Logs
1. Go to Vercel Dashboard
2. Your Project → **Functions** tab
3. Click on a function
4. View real-time logs

## 🔄 Continuous Deployment

Vercel automatically deploys when you push to:
- **main branch** → Production
- **other branches** → Preview deployments

### Setup Git Integration

1. Go to Vercel Dashboard
2. Import your Git repository
3. Connect GitHub/GitLab/Bitbucket
4. Auto-deploy on every push!

## 💰 Pricing

### Free Tier (Hobby)
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Serverless functions (100GB-hours/month)
- ✅ Perfect for development and small projects

### Pro Tier
- More bandwidth
- More function execution time
- Team collaboration
- Advanced analytics

## 🎉 Post-Deployment Checklist

- [ ] Frontend loads correctly
- [ ] Backend health check works (`/api/health`)
- [ ] API endpoints respond correctly
- [ ] Environment variables configured
- [ ] CORS configured for Vercel domain
- [ ] BigQuery connection works
- [ ] GCS access works
- [ ] Test data loading in frontend
- [ ] Monitor function logs for errors

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Python Runtime](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Next.js on Vercel](https://vercel.com/docs/concepts/frameworks/nextjs)
- [Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)

## 🆘 Need Help?

1. Check Vercel Function Logs
2. Check browser console for frontend errors
3. Verify environment variables
4. Test endpoints with curl
5. Check CORS configuration

---

**Ready to deploy? Run:**
```bash
vercel login && vercel
```

