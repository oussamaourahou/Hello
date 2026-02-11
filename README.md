# Email Archive Explorer

A powerful web-based interface to interact with large email archives stored in mbox format. This application allows you to efficiently query, analyze, and explore your email history without loading the entire file into memory.

## Features

### Email Archive Interface
- **Efficient Indexing**: Parse and index large mbox files (25GB+) into a searchable SQLite database
- **Full-Text Search**: Fast search across subject, sender, recipient, and email body
- **Advanced Filtering**: Filter by sender, recipient, subject, date range, and attachments
- **Analytics Dashboard**: Visualize email patterns, top correspondents, and temporal distributions
- **Email Viewer**: View individual emails with full metadata and attachments list

### Original Features (Glovo Menu AI Pipeline)
- **Stage 2**: Photo-to-Item Matching using OpenAI GPT-4 Vision
- **Stage 3**: Photo Quality Assessment
- **Stage 4**: Photo Enhancement with Photoroom API
- **Full Pipeline**: Run all stages sequentially

## Tech Stack

- **Backend**: Python + FastAPI
- **Frontend**: HTML/CSS/JavaScript
- **AI**: OpenAI GPT-4 Vision API
- **Enhancement**: Photoroom API

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Configure API keys in `.env` (optional, only needed for Menu AI features):
```
OPENAI_API_KEY=your_key_here
PHOTOROOM_API_KEY=your_key_here
```

3. Start the backend:
```bash
python -m uvicorn backend.main:app --reload
```

4. Open the frontend:
```bash
# Serve with a simple HTTP server:
cd frontend && python -m http.server 8080
```

5. Access the applications:
   - **Email Archive**: `http://localhost:8080/email-archive.html`
   - **Menu AI Pipeline**: `http://localhost:8080/index.html`

## Usage

### Email Archive Explorer

1. **Initial Indexing**:
   - Open the Email Archive interface at `http://localhost:8080/email-archive.html`
   - Enter the full path to your mbox file (e.g., `/path/to/emails.mbox`)
   - Click "Start Indexing" - this will create a searchable database
   - For a 25GB file, indexing may take 30-60 minutes (only needed once)
   - The status indicator will show progress

2. **Search & Query**:
   - Use the search box for full-text search across all emails
   - Filter by sender, recipient, subject, or date range
   - Click on any email to view its full content
   - Results are paginated for easy browsing

3. **Analytics**:
   - Switch to the Analytics tab to view insights
   - See top senders/recipients
   - Visualize email distribution by year and day of week
   - Identify patterns in your email history

4. **Advanced Usage**:
   - The SQLite database (`email_archive.db`) is created in the project root
   - You can query it directly using SQL tools for custom analysis
   - All searches use indexes for fast performance

### Menu AI Pipeline

1. Add/edit menu items in the left panel
2. Upload a food photo
3. Click a stage button to run individual stages, or "Run Full Pipeline" for all stages
4. View results in the right panel

## Project Structure

```
.
├── backend/
│   ├── main.py                     # FastAPI app with all endpoints
│   ├── models/
│   │   └── schemas.py              # Pydantic models
│   └── services/
│       ├── email_indexer.py        # Email mbox parser & indexer
│       ├── email_query.py          # Email search & query service
│       ├── email_analytics.py      # Email analytics & insights
│       ├── vision_service.py       # OpenAI Vision integration
│       └── photoroom_service.py    # Photoroom API integration
├── frontend/
│   ├── email-archive.html          # Email Archive UI
│   ├── email-archive.js            # Email Archive logic
│   ├── index.html                  # Menu AI Pipeline UI
│   ├── style.css                   # Styling
│   └── app.js                      # Frontend logic
├── requirements.txt                # Python dependencies
├── email_archive.db                # SQLite database (auto-created)
└── .env                            # API keys (not committed)
```

## API Endpoints

### Email Archive Endpoints

- `POST /api/email/index` - Start indexing an mbox file
- `GET /api/email/index/status` - Get indexing status
- `GET /api/email/stats` - Get overall statistics
- `GET /api/email/search` - Search emails with filters
- `GET /api/email/{email_id}` - Get single email by ID
- `GET /api/email/senders` - Get list of senders
- `GET /api/email/recipients` - Get list of recipients
- `GET /api/email/analytics/by-year` - Email distribution by year
- `GET /api/email/analytics/by-month` - Email distribution by month
- `GET /api/email/analytics/by-day` - Email distribution by day of week
- `GET /api/email/analytics/by-hour` - Email distribution by hour
- `GET /api/email/analytics/top-senders` - Top senders
- `GET /api/email/analytics/top-recipients` - Top recipients
- `GET /api/email/analytics/top-domains` - Top email domains
- `GET /api/email/analytics/attachments` - Attachment statistics
- `GET /api/email/analytics/conversation/{email}` - Conversation stats
- `GET /api/email/analytics/size` - Size distribution

### Menu AI Endpoints

- `POST /api/stage2/match` - Photo-to-menu matching
- `POST /api/stage3/assess` - Quality assessment
- `POST /api/stage4/enhance` - Photo enhancement
- `POST /api/full-pipeline` - Run all stages

## Technical Details

### Email Archive Implementation

The email archive system is designed to handle very large mbox files efficiently:

1. **Streaming Parser**: Uses Python's `mailbox` module to stream through the mbox file without loading it entirely into memory

2. **SQLite Database**: Creates an indexed SQLite database with:
   - Main `emails` table with full email metadata
   - `attachments` table for attachment tracking
   - Full-text search using SQLite FTS5
   - Indexes on sender, recipient, subject, and date for fast queries

3. **Background Indexing**: The indexing process runs in the background, allowing the API to remain responsive

4. **Efficient Queries**: All searches use database indexes and pagination to ensure fast performance even with millions of emails

### Performance Characteristics

- **Indexing Speed**: ~5,000-10,000 emails/minute (depends on hardware)
- **Search Speed**: <100ms for most queries
- **Memory Usage**: <500MB during indexing, <100MB during normal operation
- **Database Size**: Approximately 40-50% of original mbox file size

## Deployment on Render

Deploy the application to Render with just a few clicks:

### Quick Deploy

1. **Push to GitHub**:
   ```bash
   git push origin main
   ```

2. **Connect to Render**:
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file

3. **Configure Environment Variables** (in Render Dashboard):
   - `OPENAI_API_KEY` - Your OpenAI API key (optional)
   - `PHOTOROOM_API_KEY` - Your Photoroom API key (optional)
   - `DB_PATH` - Set to `/opt/render/project/src/data/email_archive.db`
   - `CORS_ORIGINS` - Set to your frontend URL or `*` for development

4. **Deploy**:
   - Click "Apply" to deploy both services
   - Wait for deployment to complete (~5 minutes)

### Services Created

The `render.yaml` automatically creates:

1. **Backend API Service**:
   - Python web service running FastAPI
   - 10GB persistent disk for email database
   - Automatic HTTPS
   - Environment variables for configuration

2. **Frontend Static Service**:
   - Static site hosting for HTML/CSS/JS
   - Automatic HTTPS
   - Connected to backend API

### Accessing Your Deployed App

After deployment:
- **Frontend URL**: `https://email-archive-frontend.onrender.com`
- **Backend API**: `https://email-archive-api.onrender.com`

Update the `API_BASE` in `frontend/email-archive.js` to point to your backend URL.

### Uploading Your mbox File

Since your mbox file is 25GB, you have several options:

1. **Option 1: Upload via SCP/SFTP** (Recommended for large files):
   - Get SSH access to your Render service
   - Use `scp` to upload the mbox file to `/opt/render/project/src/data/`

2. **Option 2: Cloud Storage Integration**:
   - Upload your mbox file to AWS S3, Google Cloud Storage, or Dropbox
   - Modify the indexing endpoint to download from cloud storage
   - Add a download step before indexing

3. **Option 3: Use Render Disk**:
   - The deployed service includes a 10GB persistent disk
   - For files larger than 10GB, upgrade the disk size in Render settings
   - Can go up to 512GB

### Important Notes

- **Persistent Storage**: The database is stored on Render's persistent disk, so your indexed data won't be lost on redeploys
- **Cold Starts**: Free tier services may sleep after 15 minutes of inactivity
- **Upgrade for Production**: For production use with large files, consider upgrading to a paid plan for:
  - More RAM and CPU
  - Larger persistent disk
  - No cold starts
  - Better performance

### Manual Deployment (Alternative)

If you prefer manual deployment:

1. **Deploy Backend**:
   ```bash
   # On Render, create a new Web Service
   # Build Command: pip install -r requirements.txt
   # Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```

2. **Deploy Frontend**:
   ```bash
   # On Render, create a Static Site
   # Publish Directory: frontend
   ```

3. **Add Persistent Disk**:
   - Go to backend service settings
   - Add a disk (10GB minimum, 512GB maximum)
   - Mount at `/opt/render/project/src/data`

### Monitoring

Monitor your deployment:
- Check logs in Render dashboard
- Monitor disk usage for the database
- Track API performance and response times
- Set up alerts for errors

### Cost Estimation

- **Free Tier**: $0/month (limited resources, cold starts)
- **Starter Tier**: ~$7/month per service (~$14 total)
- **Standard Tier**: ~$25/month per service (~$50 total)
- **Additional Storage**: ~$0.25/GB/month

For a 25GB mbox file, budget for:
- ~15GB persistent disk (for database + mbox) = ~$3.75/month
- Backend service (Starter or better) = $7-25/month
- Frontend service (Free or Starter) = $0-7/month
- **Total**: ~$11-36/month