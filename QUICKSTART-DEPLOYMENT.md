# Quick Start: Deploy to Render

Complete guide to deploy your Planning Poker app to Render in ~10 minutes.

## What I've Set Up For You

✅ Git repository initialized
✅ All code committed
✅ Backend configured for production (Redis URL support)
✅ Frontend configured for production (environment variables)
✅ Render deployment script (`deploy-render.py`)
✅ Render blueprint configuration (`render.yaml`)
✅ GitHub setup helper script (`setup-github.sh`)

## Your 6-Step Deployment Process

### Step 1: Create GitHub Repository (2 minutes)

**Option A: Using GitHub CLI (Recommended)**
```bash
./setup-github.sh
```

The script will:
- Check if you have GitHub CLI installed
- Authenticate if needed
- Create the repository
- Push your code

**Option B: Manual Setup**
```bash
# 1. Create repo at https://github.com/new (name: planning-poker)
# 2. Then run:
git remote add origin https://github.com/YOUR_USERNAME/planning-poker.git
git branch -M main
git push -u origin main
```

### Step 2: Create Render Account (1 minute)

1. Go to https://render.com
2. Sign up (free tier available)
3. Verify email

### Step 3: Generate Render API Key (1 minute)

1. Go to https://dashboard.render.com/
2. Click your profile → **Account Settings**
3. Navigate to **API Keys**
4. Click **Create API Key**
5. Name it "Planning Poker Deployment"
6. **Copy the key** (shown only once!)

### Step 4: Connect GitHub to Render (1 minute)

**CRITICAL**: One-time OAuth setup

1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**
3. Click **Connect GitHub**
4. Authorize Render
5. Click **Cancel** (we just needed the connection)

### Step 5: Set Environment Variables (30 seconds)

```bash
# Replace with your actual values
export RENDER_API_KEY='rnd_xxxxxxxxxxxxxxxxxxxxx'
export GITHUB_REPO_URL='https://github.com/YOUR_USERNAME/planning-poker'
```

### Step 6: Deploy! (30 seconds + 5-10 min build time)

```bash
# Install requests library if needed
pip install requests

# Run deployment
./deploy-render.py
```

The script will automatically:
- Create Redis instance
- Create backend web service
- Create frontend static site
- Configure all environment variables
- Set up CORS between services

## What You'll Get

After deployment completes (5-10 minutes):

```
Frontend: https://planning-poker-frontend.onrender.com
Backend:  https://planning-poker-backend.onrender.com
```

## Monitoring Your Deployment

1. Go to https://dashboard.render.com/
2. You'll see 3 services:
   - `planning-poker-redis` (Redis)
   - `planning-poker-backend` (Web Service)
   - `planning-poker-frontend` (Static Site)
3. Click each to view build logs

## Troubleshooting

### "GitHub repository not found"
- Make sure you completed Step 4 (Connect GitHub to Render)
- Verify the repository URL is correct
- Ensure repo is public (or Render has access if private)

### "Build failed"
- Click on the failing service in Render dashboard
- Check the build logs for specific errors
- Common issues:
  - Missing dependencies
  - Syntax errors
  - Wrong build commands

### "Frontend can't connect to backend"
- Check browser console for errors
- Verify environment variables are set correctly in Render dashboard
- Give it a few minutes - DNS propagation can take time

### "Cold starts are slow"
- This is normal on Render's free tier
- Services sleep after 15 minutes of inactivity
- First request takes ~30 seconds to wake up
- Upgrade to paid plan to avoid this

## Free Tier Limits

- ✅ 750 hours/month per service
- ✅ Redis: 25 MB storage
- ✅ Automatic SSL/HTTPS
- ⚠️  Services sleep after 15 min inactivity
- ⚠️  Cold starts take ~30 seconds

Perfect for demo/testing, upgrade for production use.

## Manual Deployment (Alternative)

If you prefer clicking through the Render UI instead of using the script, see the detailed manual instructions in `DEPLOYMENT.md`.

## Updating Your App

After making code changes:

```bash
git add .
git commit -m "Your changes"
git push
```

Render automatically rebuilds and redeploys (auto-deploy is enabled).

## Cost

**Free tier**: $0/month
- Perfect for demos and testing
- Includes everything you need

**Paid tier**: ~$7/month
- No cold starts
- More resources
- Better for production

## Next Steps After Deployment

1. ✅ Test your app at the frontend URL
2. ✅ Create a room and verify WebSocket connection
3. ✅ Test voting functionality
4. ✅ Share the URL with your team!

## Need Help?

- Full deployment guide: See `DEPLOYMENT.md`
- Render docs: https://render.com/docs
- Issues: Create an issue in your GitHub repo

---

**Ready to deploy?** Start with Step 1! 🚀
