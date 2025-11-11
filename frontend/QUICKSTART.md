# Quick Start Guide

## Installation

```bash
cd frontend
npm install
```

## Development

1. Make sure the backend is running on `http://localhost:8000`
2. Start the Next.js dev server:

```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Usage

1. **Select Dates**: Choose old and new dates using the date pickers
2. **Set Limit**: Choose how many results to display (50, 100, 200, 500)
3. **Auto-Fetch**: Toggle to automatically download and process missing dates
4. **Load Data**: Click to fetch field comparison data
5. **Stats**: Click to view summary statistics
6. **Navigate**: Use Previous/Next buttons to paginate through results

## Features

- ✅ Automatic date fetching when data is missing
- ✅ Real-time statistics
- ✅ Pagination support
- ✅ Responsive design
- ✅ Error handling

## Troubleshooting

### Backend Connection Error

If you see connection errors:
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local` (defaults to `http://localhost:8000`)

### CORS Issues

If you see CORS errors, make sure the backend allows requests from `http://localhost:3000`

