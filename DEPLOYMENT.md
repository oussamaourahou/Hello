# Deployment Guide

This guide covers deploying the Email Archive Explorer to Render.

## Prerequisites

- GitHub account
- Render account (free at [render.com](https://render.com))
- Your mbox email archive file

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure all files are committed and pushed to GitHub:

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. Deploy to Render

#### Using Blueprint (Recommended)

1. Log in to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account if not already connected
4. Select your repository
5. Render will detect `render.yaml` automatically
6. Click **"Apply"** to create services

#### Manual Deployment

If you prefer manual setup:

**Backend Service:**
1. New → Web Service
2. Connect your repository
3. Configure:
   - **Name**: `email-archive-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2`
   - **Plan**: Starter ($7/month) or higher

4. Add Persistent Disk:
   - Go to service Settings
   - Add Disk: 10GB (or more for large files)
   - Mount Path: `/opt/render/project/src/data`

**Frontend Service:**
1. New → Static Site
2. Connect your repository
3. Configure:
   - **Name**: `email-archive-frontend`
   - **Publish Directory**: `frontend`
   - **Build Command**: (leave empty)

### 3. Configure Environment Variables

In the backend service settings, add these environment variables:

| Variable | Value | Required |
|----------|-------|----------|
| `DB_PATH` | `/opt/render/project/src/data/email_archive.db` | Yes |
| `OPENAI_API_KEY` | Your OpenAI API key | No (only for Menu AI) |
| `PHOTOROOM_API_KEY` | Your Photoroom API key | No (only for Menu AI) |
| `CORS_ORIGINS` | `*` | Yes |

### 4. Upload Your mbox File

Since your file is 25GB, you have these options:

#### Option A: Via Render Shell (Recommended)

1. Go to your backend service in Render
2. Click **"Shell"** tab
3. You'll get SSH access to your service
4. Use `scp` or upload tools to transfer your file:

```bash
# From your local machine
scp /path/to/emails.mbox render@your-service:/opt/render/project/src/data/
```

#### Option B: Cloud Storage Integration

1. Upload mbox to S3/GCS/Dropbox
2. In Render Shell, download it:

```bash
cd /opt/render/project/src/data
wget https://your-cloud-storage-url/emails.mbox
```

#### Option C: Split and Upload

For very large files:

```bash
# Split locally
split -b 1G emails.mbox emails.mbox.part

# Upload parts via Render Shell
# Reassemble on Render:
cat emails.mbox.part* > emails.mbox
```

### 5. Index Your Emails

1. Once your file is uploaded, open your deployed frontend:
   - URL: `https://your-frontend-name.onrender.com/email-archive.html`

2. Start indexing:
   - Enter path: `/opt/render/project/src/data/emails.mbox`
   - Click "Start Indexing"
   - Wait for completion (check backend logs)

3. For a 25GB file:
   - Expected time: 1-2 hours
   - Database size: ~10-12GB
   - Ensure you have sufficient disk space

### 6. Verify Deployment

Check that everything works:

- [ ] Frontend loads correctly
- [ ] Backend API responds (visit `/api/email/stats`)
- [ ] Indexing completes without errors
- [ ] Search functionality works
- [ ] Analytics display correctly

### 7. Update Frontend API URL (If Needed)

If using custom domains or the auto-detection doesn't work:

Edit `frontend/email-archive.js`:

```javascript
const API_BASE = 'https://your-backend-url.onrender.com/api';
```

Then redeploy the frontend service.

## Troubleshooting

### Database Connection Errors

- Verify `DB_PATH` environment variable
- Check disk is properly mounted
- Ensure disk has enough space

### CORS Errors

- Verify `CORS_ORIGINS` is set to `*` or includes your frontend URL
- Check backend logs for CORS-related errors

### Out of Memory

- Upgrade to a plan with more RAM
- Reduce batch size in indexing (modify `batch_size` parameter)

### File Upload Issues

- Ensure persistent disk is large enough
- Check disk mount path is correct
- Verify file permissions

### Cold Starts (Free Tier)

- Services sleep after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- Upgrade to paid plan to eliminate cold starts

## Monitoring

### Logs

- Backend: View in Render dashboard → Service → Logs
- Look for indexing progress messages
- Monitor for errors or warnings

### Disk Usage

```bash
# In Render Shell
df -h /opt/render/project/src/data
du -h /opt/render/project/src/data/email_archive.db
```

### Performance

- Check API response times in browser dev tools
- Monitor indexing speed in logs
- Track memory usage in Render metrics

## Scaling Considerations

For production use with large files:

1. **Upgrade Service Plan**:
   - More RAM for faster indexing
   - More CPU for better search performance
   - No cold starts

2. **Increase Disk Size**:
   - Start with 2x your mbox file size
   - Can upgrade anytime in Render settings

3. **Database Optimization**:
   - Database is already optimized with indexes
   - Consider archiving old emails if needed

4. **Caching**:
   - Add Redis for API response caching
   - Cache frequently accessed queries

## Cost Management

Estimated monthly costs:

| Configuration | Cost/Month |
|--------------|------------|
| Free Tier (both services) | $0 (limited) |
| Starter Backend + Free Frontend | $7 |
| Starter Both Services | $14 |
| Standard Backend + Starter Frontend | $32 |

Plus storage: ~$0.25/GB/month

For 25GB mbox (needs ~15GB disk): +$3.75/month

## Security Best Practices

1. **Environment Variables**:
   - Never commit `.env` files
   - Use Render's environment variable system

2. **CORS**:
   - In production, set specific origins instead of `*`
   - `CORS_ORIGINS=https://your-domain.com`

3. **API Keys**:
   - Keep API keys secret
   - Rotate regularly
   - Use Render's secret management

4. **Database**:
   - Database is on private network
   - Not publicly accessible
   - Backed up with disk snapshots

## Backup Strategy

1. **Database Snapshots**:
   - Take periodic snapshots of persistent disk
   - Render provides disk snapshots in paid plans

2. **Export Data**:
   ```bash
   # In Render Shell
   sqlite3 /opt/render/project/src/data/email_archive.db .dump > backup.sql
   ```

3. **Backup mbox**:
   - Keep original mbox file in safe location
   - Can re-index if needed

## Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **GitHub Issues**: Report bugs in repository
- **Email Archive Docs**: See main README.md

## Next Steps

After successful deployment:

1. Set up custom domain (optional)
2. Configure backup schedule
3. Monitor usage and costs
4. Optimize based on usage patterns
5. Consider adding authentication for production use
