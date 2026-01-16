# Glovo Menu AI Pipeline

AI-powered restaurant menu photo processing system that matches food photos to menu items, assesses quality, and enhances images.

## Features

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

2. Configure API keys in `.env`:
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
# Open frontend/index.html in your browser
# Or serve with a simple HTTP server:
cd frontend && python -m http.server 8080
```

5. Access the app at `http://localhost:8080`

## Usage

1. Add/edit menu items in the left panel
2. Upload a food photo
3. Click a stage button to run individual stages, or "Run Full Pipeline" for all stages
4. View results in the right panel

## Project Structure

```
.
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── services/
│       ├── vision_service.py   # OpenAI Vision integration
│       └── photoroom_service.py # Photoroom API integration
├── frontend/
│   ├── index.html              # Main UI
│   ├── style.css               # Styling
│   └── app.js                  # Frontend logic
├── requirements.txt            # Python dependencies
└── .env                        # API keys (not committed)
```