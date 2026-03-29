# OpenFang Auto Clip - Web Dashboard

Web-based dashboard for OpenFang Auto Clip.

## Development Setup

### Prerequisites
- Node.js 18+
- npm or yarn

### Installation

```bash
cd web
npm install
```

### Development

```bash
npm run dev
```

The dashboard will be available at http://localhost:5173

### Build

```bash
npm run build
```

### Production Preview

```bash
npm run preview
```

## Tech Stack

- **Vue.js 3** - Progressive JavaScript framework
- **Vite** - Next generation frontend tooling
- **Element Plus** - Vue 3 UI library
- **Axios** - HTTP client
- **Pinia** - State management
- **Vue Router** - Routing

## Features

- 📊 Home page with project overview
- 🎬 Process video/transcript
- 📋 Job management and tracking
- 🔍 Level 2 package validation
- 📱 Responsive design

## API Configuration

The API base URL is configured via environment variable:

```bash
VITE_API_URL=http://localhost:8000
```

Or set in `.env` file.
