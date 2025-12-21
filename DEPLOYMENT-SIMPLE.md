# Simple Render Deployment (Free Tier)

**TL;DR**: Render's API doesn't support free tier services. Use the UI with the `render.yaml` blueprint instead - it's actually simpler!

## Why This Method?

The Render API requires paid plans for programmatic deployment. But deploying via the UI with our `render.yaml` file:
- ✅ Supports free tier
- ✅ Creates all 3 services at once
- ✅ Auto-configures environment variables
- ✅ Takes ~2 minutes of clicking

## Prerequisites

1. **GitHub account** with your code pushed
2. **Render account** (free) - https://render.com

## Deployment Steps

### 1. Push Code to GitHub (if not done already)

```bash
# If you haven't set up GitHub yet:
./setup-github.sh

# Or manually:
git remote add origin https://github.com/YOUR_USERNAME/planning-poker.git
git branch -M main
git push -u origin main
```

### 2. Deploy via Render UI

1. **Go to Render Dashboard**: https://dashboard.render.com/

2. **Click "New +" → "Blueprint"**

3. **Connect Your Repository**:
   - Click "Connect account" if not already connected
   - Select your `planning-poker` repository
   - Click "Connect"

4. **Configure Blueprint**:
   - Render will detect `render.yaml` automatically
   - Service names will be pre-filled
   - Click "Apply"

5. **Set Frontend CORS** (one-time manual step):
   - After services are created, go to `planning-poker-backend`
   - Go to "Environment" tab
   - Find `CORS_ORIGINS` variable
   - Set value to: `https://planning-poker-frontend.onrender.com`
   - Click "Save Changes"

### 3. Wait for Builds

- Redis: ~1 minute (instant)
- Backend: ~5 minutes (pip install + deploy)
- Frontend: ~3 minutes (npm install + build)

### 4. Get Your URLs

Once deployed, you'll see:
- **Frontend**: `https://planning-poker-frontend.onrender.com`
- **Backend**: `https://planning-poker-backend.onrender.com`

Click the frontend URL to use your app!

## What Gets Created

The `render.yaml` file automatically creates:

| Service | Type | What It Does |
|---------|------|--------------|
| planning-poker-redis | Redis | Stores room data (25MB free) |
| planning-poker-backend | Web Service | Python FastAPI + WebSockets |
| planning-poker-frontend | Static Site | React app |

## Environment Variables

These are auto-configured by `render.yaml`:

**Backend**:
- `REDIS_URL` - Automatically linked to Redis
- `ENVIRONMENT` - Set to "production"
- `LOG_LEVEL` - Set to "INFO"
- `CORS_ORIGINS` - **Set this manually** to frontend URL

**Frontend**:
- `VITE_WS_URL` - Automatically set to backend URL
- `VITE_API_URL` - Automatically set to backend URL

## Troubleshooting

### "Repository not found"
- Make sure you connected GitHub to Render
- Check repository visibility (public or Render has access)

### "Build failed"
**Backend**:
- Check if `requirements.txt` exists in `backend/` folder
- View build logs for specific errors

**Frontend**:
- Check if `package.json` exists in `frontend/` folder
- Ensure `dist` folder is created during build

### "CORS error in browser"
- Make sure you set `CORS_ORIGINS` in backend
- Should be: `https://planning-poker-frontend.onrender.com`
- Redeploy backend after changing

### "Can't connect to WebSocket"
- Check browser console for errors
- Verify `VITE_WS_URL` is set correctly in frontend
- Should be: `https://planning-poker-backend.onrender.com`

## Free Tier Limitations

- ✅ 750 hours/month per service (enough for 24/7)
- ✅ 25MB Redis storage
- ✅ Automatic HTTPS
- ⚠️ Services sleep after 15 minutes of inactivity
- ⚠️ Cold start takes ~30 seconds on first request

Perfect for demos and testing. Upgrade to paid ($7/month) for no cold starts.

## Updating Your App

To deploy changes:

```bash
git add .
git commit -m "Your changes"
git push
```

Render auto-deploys on push (this is configured in `render.yaml`).

## Alternative: Manual Service Creation

If you prefer to create services one-by-one instead of using the Blueprint:

1. **Create Redis first**
2. **Create Backend** (link to Redis)
3. **Create Frontend** (link to Backend)

See `DEPLOYMENT.md` for detailed manual steps.

## Cost Breakdown

**Free Tier**: $0/month
- 3 services (Redis + Backend + Frontend)
- 750 hours/month each
- Auto-sleep after 15 min
- Perfect for demos

**Paid Tier**: ~$21/month
- Redis: $7/month (no sleep)
- Backend: $7/month (no sleep)
- Frontend: $0 (static sites are free!)
- No cold starts
- Better for production

## Need Help?

- Check build logs in Render dashboard
- See full docs: `DEPLOYMENT.md`
- Render support: https://render.com/docs
