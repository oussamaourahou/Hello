# Deployment Guide

This application can be deployed to Railway or Render with just a few clicks.

## Option 1: Deploy to Railway (Recommended - Easiest)

Railway offers the simplest deployment process:

### Steps:

1. **Push your code to GitHub** (already done!)

2. **Go to Railway**: https://railway.app/

3. **Sign in with GitHub**

4. **Click "New Project"** → **"Deploy from GitHub repo"**

5. **Select this repository**: `oussamaourahou/Hello`

6. **Add Environment Variables**:
   - Click on your service → Variables tab
   - Add these variables:
     - `OPENAI_API_KEY`: (your OpenAI API key)
     - `PHOTOROOM_API_KEY`: (your Photoroom API key)

7. **Deploy!** Railway will automatically:
   - Detect the Dockerfile
   - Build and deploy your app
   - Give you a public URL

8. **Access your app** at the URL Railway provides (e.g., `https://your-app.railway.app`)

### Cost:
- Free tier: $5 credit per month
- Should be enough for testing and light usage

---

## Option 2: Deploy to Render

Render is another great option with a generous free tier:

### Steps:

1. **Push your code to GitHub** (already done!)

2. **Go to Render**: https://render.com/

3. **Sign in with GitHub**

4. **Click "New +"** → **"Web Service"**

5. **Connect your repository**: `oussamaourahou/Hello`

6. **Configure**:
   - Name: `glovo-menu-ai`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`

7. **Add Environment Variables**:
   - `OPENAI_API_KEY`: (your OpenAI API key)
   - `PHOTOROOM_API_KEY`: (your Photoroom API key)

8. **Deploy!** Render will build and deploy your app

9. **Access your app** at the URL Render provides (e.g., `https://glovo-menu-ai.onrender.com`)

### Cost:
- Free tier available
- App may spin down after inactivity (takes ~30s to restart)

---

## Quick Test After Deployment

Once deployed, visit your app URL and:

1. The frontend should load automatically
2. Add menu items or use the pre-loaded ones
3. Upload a food photo
4. Click "Stage 2: Match Photo" to test
5. Try other stages or the full pipeline

---

## Troubleshooting

### If the app doesn't work:

1. **Check Environment Variables**: Make sure both API keys are set correctly
2. **Check Logs**: Both Railway and Render have log viewers to see errors
3. **Check Build**: Make sure the build completed successfully

### Common Issues:

- **API errors**: Verify your OpenAI and Photoroom API keys are valid
- **CORS errors**: Should not happen with this setup, but check browser console
- **500 errors**: Check the backend logs for detailed error messages
