# Render Deployment Guide

This guide covers deploying the Planning Poker app to Render using the automated deployment script.

## Prerequisites

1. **Render Account**: Sign up at https://render.com (free tier available)
2. **GitHub Account**: Repository must be on GitHub
3. **Python 3.7+**: For running the deployment script
4. **Requests library**: `pip install requests`

## Step 1: Create Render Account

1. Go to https://render.com
2. Sign up for a free account
3. Verify your email

## Step 2: Create Render API Key

1. Go to https://dashboard.render.com/
2. Click on your profile → Account Settings
3. Navigate to **API Keys** section
4. Click **Create API Key**
5. Give it a name (e.g., "Planning Poker Deployment")
6. Copy the API key (you won't see it again!)

## Step 3: Connect GitHub to Render

**IMPORTANT**: You must connect your GitHub account to Render before the script can deploy.

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Click **Connect GitHub** (this is a one-time OAuth authorization)
4. Authorize Render to access your repositories
5. **Cancel** the service creation (we just needed to connect GitHub)

## Step 4: Create GitHub Repository

If you haven't already pushed the code to GitHub:

```bash
# Create a new repository on GitHub (via web interface)
# Then push your code:

git remote add origin https://github.com/YOUR_USERNAME/planning-poker.git
git branch -M main
git push -u origin main
```

## Step 5: Set Environment Variables

```bash
# Set your Render API key
export RENDER_API_KEY='rnd_xxxxxxxxxxxxxxxxxxxxx'

# Set your GitHub repository URL
export GITHUB_REPO_URL='https://github.com/YOUR_USERNAME/planning-poker'
```

## Step 6: Run Deployment Script

```bash
# Make script executable
chmod +x deploy-render.py

# Install required package
pip install requests

# Run deployment
python3 deploy-render.py
```

The script will:
1. Create a Redis instance
2. Create the backend web service
3. Create the frontend static site
4. Configure environment variables automatically
5. Set up proper CORS between frontend and backend

## Step 7: Monitor Deployment

1. Go to https://dashboard.render.com/
2. You should see three services:
   - `planning-poker-redis` (Redis)
   - `planning-poker-backend` (Web Service)
   - `planning-poker-frontend` (Static Site)

3. Click on each service to monitor build progress
4. Initial builds take ~5-10 minutes

## Step 8: Access Your App

Once deployment completes, you'll see the URLs in the script output:

```
Frontend: https://planning-poker-frontend.onrender.com
Backend:  https://planning-poker-backend.onrender.com
```

Visit the frontend URL to use your deployed app!

## Troubleshooting

### Build Failures

**Backend build fails:**
- Check `requirements.txt` is present in `backend/` directory
- View logs in Render dashboard

**Frontend build fails:**
- Check `package.json` is present in `frontend/` directory
- Ensure build script is: `npm install && npm run build`

### Runtime Errors

**Backend can't connect to Redis:**
- Check that `REDIS_URL` environment variable is set correctly
- Redis should be in the same region as your backend

**Frontend can't connect to backend:**
- Check CORS settings in backend
- Verify `VITE_WS_URL` and `VITE_API_URL` are set correctly
- Check browser console for errors

### CORS Issues

If you see CORS errors in the browser console:

1. Go to backend service settings
2. Check `CORS_ORIGINS` environment variable includes your frontend URL
3. Should be: `https://planning-poker-frontend.onrender.com`

## Manual Deployment (Alternative)

If you prefer to deploy manually via Render UI instead of the script:

### 1. Create Redis
- Dashboard → New → Redis
- Name: `planning-poker-redis`
- Plan: Free
- Copy the **Internal Connection String**

### 2. Create Backend
- Dashboard → New → Web Service
- Connect your repository
- Name: `planning-poker-backend`
- Root Directory: `backend`
- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Plan: Free

**Environment Variables:**
```
REDIS_URL=<paste Internal Connection String from Redis>
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://planning-poker-frontend.onrender.com
```

### 3. Create Frontend
- Dashboard → New → Static Site
- Connect same repository
- Name: `planning-poker-frontend`
- Root Directory: `frontend`
- Build Command: `npm install && npm run build`
- Publish Directory: `dist`
- Plan: Free

**Environment Variables:**
```
VITE_WS_URL=https://planning-poker-backend.onrender.com
VITE_API_URL=https://planning-poker-backend.onrender.com
```

## Free Tier Limitations

Render's free tier includes:

- ✅ 750 hours/month per service
- ✅ Auto-sleep after 15 minutes of inactivity
- ✅ First request after sleep takes ~30 seconds (cold start)
- ✅ Redis: 25 MB storage
- ✅ Automatic SSL certificates

For production use, consider upgrading to paid plans to avoid cold starts.

## Updating Your Deployment

After pushing changes to GitHub:

```bash
git add .
git commit -m "Your changes"
git push
```

Render will automatically rebuild and redeploy (auto-deploy is enabled).

To disable auto-deploy:
- Go to service settings
- Turn off "Auto-Deploy"

## Useful Commands

### View Logs
```bash
# In Render dashboard, click on service → Logs tab
```

### Manual Deploy Trigger
```bash
# In Render dashboard, click on service → Manual Deploy
```

### Delete All Services
```bash
# Go to each service → Settings → Delete Service
```

## Support

- Render Documentation: https://render.com/docs
- Render Community: https://community.render.com/
- GitHub Issues: [Your repo URL]/issues
