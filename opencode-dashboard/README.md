# OpenCode Usage Dashboard

Real-time dashboard for tracking OpenCode LLM usage, costs, and token analytics.

## Features

- **Live Data** - Reads directly from OpenCode message storage, no manual parsing needed
- **Cost Analytics** - Track spending by model, provider, and time period
- **Token Tracking** - Monitor input, output, and cache token usage
- **Session History** - View all OpenCode sessions with detailed metrics
- **Custom Date Ranges** - Analyze usage over 7, 14, 30, 60, or 90 days
- **Provider Breakdown** - Compare costs across AWS Bedrock, Google AI Studio, etc.
- **Model Comparison** - See which models (Claude, Gemini) cost the most
- **Cache Efficiency** - Track LLM prompt caching hit rates and savings

## Quick Start

```bash
# Install dependencies
npm install

# Start the dashboard server
npm start
```

Then open http://localhost:3030 in your browser.

## Requirements

- Node.js 18 or higher
- OpenCode CLI installed with message data in `~/.local/share/opencode/storage/message/`

## How It Works

1. **Backend Server** (`server.js`)
   - Express server on port 3030
   - Reads and parses OpenCode message JSON files on-demand
   - Provides `/api/data` endpoint with aggregated metrics

2. **Frontend Dashboard** (`index.html` + `dashboard.js`)
   - Single-page application with multiple views
   - Fetches live data from API on page load
   - Chart.js for visualizations
   - Tailwind CSS (via CDN) for styling

## API

### Get Dashboard Data

```
GET /api/data?days=30
```

**Query Parameters:**
- `days` - Number of days to include (default: 7)
- `start` - Start date (YYYY-MM-DD)
- `end` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "totals": {
    "cost": 223.33,
    "tokens": 135576636,
    "inputTokens": 66006388,
    "outputTokens": 1029506,
    "cacheReadTokens": 65370616,
    "sessionCount": 114
  },
  "models": [...],
  "providers": [...],
  "sessions": [...],
  "dailyCosts": {
    "labels": ["Dec 15", "Dec 22", ...],
    "datasets": { ... }
  }
}
```

## File Structure

```
opencode-dashboard/
├── server.js          # Backend Express server
├── index.html         # Dashboard HTML
├── dashboard.js       # Frontend JavaScript
├── package.json       # Dependencies
└── README.md          # This file
```

## Development

The dashboard auto-refreshes data on each page load. Just refresh your browser to see the latest OpenCode usage.

To modify:
- **Backend logic**: Edit `server.js`
- **UI/styling**: Edit `index.html`
- **Dashboard logic**: Edit `dashboard.js`

Then restart the server:
```bash
# Stop with Ctrl+C
npm start
```

## License

ISC
