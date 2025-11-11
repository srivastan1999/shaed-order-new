# SHAED Order ELT - Frontend

Next.js frontend for the SHAED Order ELT Ford Field Comparison tool.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Deploy to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd frontend
vercel
```

Or use the [Vercel Dashboard](https://vercel.com/new) to deploy your project.

## 📋 Features

- 📅 Date selection for comparing Ford order fields
- 🔄 Automatic download and processing of missing dates
- 📊 Statistics dashboard
- 📋 Data table with pagination
- 🎨 Modern UI with Tailwind CSS
- 📱 Responsive design

## 🔧 Configuration

### Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For Vercel, set in Dashboard → Settings → Environment Variables.

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Home page
│   └── globals.css     # Global styles
├── components/
│   └── FieldComparison.tsx  # Main comparison component
├── lib/
│   └── api.ts         # API client
└── package.json
```

## 🌐 API Integration

The frontend connects to:
- `GET /health` - Health check
- `GET /api/ford-field-comparison` - Field comparison
- `GET /api/ford-field-comparison/stats` - Statistics
- `GET /api/ford-process-date` - Process date

## 🚢 Deployment

See [VERCEL_DEPLOY.md](../VERCEL_DEPLOY.md) for detailed deployment instructions.

## 📚 Documentation

- [Next.js Docs](https://nextjs.org/docs)
- [Vercel Deployment](https://vercel.com/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
