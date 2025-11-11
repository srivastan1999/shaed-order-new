# 🚀 Deploy Now - Quick Steps

## ✅ What's Done

- ✅ Vercel CLI installed
- ✅ Ready to deploy!

## Step 1: Deploy to Vercel

### Option A: Vercel CLI (Fastest - Do This Now!)

```bash
cd /Users/srivastand/Desktop/vikridProjects/shaed_order_elt/frontend

# Login to Vercel
vercel login

# Deploy (first time)
vercel

# Follow the prompts:
# - Set up and deploy? → Yes
# - Which scope? → Select your account
# - Link to existing project? → No
# - Project name? → shaed-order-elt-frontend
# - Directory? → ./
# - Override settings? → No

# After first deploy, deploy to production:
vercel --prod
```

### Option B: Vercel Dashboard

1. Go to https://vercel.com/new
2. Click "Import Project"
3. Upload your project or connect via CLI
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework**: Next.js (auto-detected)
5. **Add Environment Variable**:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `http://localhost:8000` (update later with your backend URL)
6. Click **Deploy**

## Step 3: Configure Environment Variables

After deployment, in Vercel Dashboard:

1. Go to your project → Settings → Environment Variables
2. Add:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.com
   ```
3. Redeploy (or it will auto-deploy on next push)

## Step 4: Get Your Deployment URL

After deployment, Vercel will give you:
- Production: `https://your-app.vercel.app`
- Preview: `https://your-app-git-branch.vercel.app`

## ✅ Quick Deploy Command

Run this now:

```bash
cd /Users/srivastand/Desktop/vikridProjects/shaed_order_elt/frontend
vercel login && vercel
```

## Next Steps After Deployment

1. ✅ Frontend deployed
2. ⏭️ Deploy backend (see DEPLOYMENT.md)
3. ⏭️ Update `NEXT_PUBLIC_API_URL` with backend URL
4. ⏭️ Update backend CORS with Vercel URL
5. ⏭️ Test the application

## Need Help?

- See `VERCEL_DEPLOY.md` for detailed guide
- See `DEPLOYMENT.md` for backend deployment
