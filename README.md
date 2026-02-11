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