# Vercel Deployment Guide

Quick guide to deploy the Next.js frontend to Vercel.

## Quick Deploy

### Option 1: Vercel CLI (Recommended)

```bash
# Install Vercel CLI globally
npm i -g vercel

# Navigate to frontend directory
cd frontend

# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Deploy to production
vercel --prod
```

### Option 2: Vercel Dashboard

1. **Import to Vercel**
   - Go to https://vercel.com/new
   - Click "Import Project"
   - Upload your project or connect via CLI
   - Configure:
     - **Framework Preset**: Next.js (auto-detected)
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build` (auto-detected)
     - **Output Directory**: `.next` (auto-detected)

2. **Add Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-api.com
     ```
   - For each environment (Production, Preview, Development)

3. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy

## Environment Variables

### Required

- `NEXT_PUBLIC_API_URL`: Your backend API URL
  - Development: `http://localhost:8000`
  - Production: `https://your-backend-api.com`

### Setting in Vercel

1. Go to your project in Vercel Dashboard
2. Settings → Environment Variables
3. Add variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: Your backend URL
   - **Environment**: Select all (Production, Preview, Development)

## Backend CORS Configuration

Update your backend to allow your Vercel domain:

```python
# In backend/main.py or set environment variable
ALLOWED_ORIGINS=https://your-app.vercel.app,https://your-app-git-main.vercel.app
```

Or set in your backend deployment:
```bash
export ALLOWED_ORIGINS="https://your-app.vercel.app"
```

## Custom Domain

1. Go to Project Settings → Domains
2. Add your domain (e.g., `app.yourdomain.com`)
3. Follow DNS configuration instructions
4. Update `NEXT_PUBLIC_API_URL` if needed

## Preview Deployments

Vercel can create preview deployments for different environments when configured.

Each gets a unique URL like: `https://your-app-*.vercel.app`

## Production Deployment

- **Manual**: `vercel --prod` from CLI
- **Dashboard**: Deployments → Promote to Production

## Monitoring

### Analytics

1. Go to Project → Analytics
2. Enable Vercel Analytics
3. View real-time metrics

### Logs

1. Go to Project → Deployments
2. Click on a deployment
3. View build logs and runtime logs

## Troubleshooting

### Build Fails

1. Check build logs in Vercel dashboard
2. Verify Node.js version (Vercel uses 18.x by default)
3. Check `package.json` dependencies
4. Verify build command: `npm run build`

### API Connection Issues

1. Verify `NEXT_PUBLIC_API_URL` is set correctly
2. Test backend: `curl https://your-backend.com/health`
3. Check CORS configuration on backend
4. Verify backend allows Vercel domain

### Environment Variables Not Working

1. Ensure variable name starts with `NEXT_PUBLIC_` for client-side access
2. Redeploy after adding variables
3. Check variable is set for correct environment

## Continuous Deployment

Vercel provides:
- ✅ Manual and automated deployments
- ✅ Runs builds in parallel
- ✅ Provides instant rollbacks

## Performance

Vercel automatically:
- ✅ Optimizes images
- ✅ Enables CDN caching
- ✅ Provides edge functions
- ✅ Optimizes bundle size

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ✅ Configure environment variables
3. ✅ Update backend CORS
4. ✅ Test production deployment
5. ✅ Set up custom domain (optional)
6. ✅ Enable analytics (optional)

## Support

- Vercel Docs: https://vercel.com/docs
- Vercel Discord: https://vercel.com/discord
- Status: https://vercel-status.com

