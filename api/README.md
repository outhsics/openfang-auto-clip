# OpenFang Auto Clip - REST API

REST API for OpenFang Auto Clip operations.

## Development Setup

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
cd api
pip install -r requirements.txt
```

### Development

```bash
python -m api.main
```

The API will be available at http://localhost:8000

### API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Endpoints

### Health
- `GET /api/v1/health` - Health check

### Process
- `POST /api/v1/process` - Process video/transcript

### Jobs
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/{id}` - Get job details
- `DELETE /api/v1/jobs/{id}` - Delete job

### Validate
- `POST /api/v1/validate` - Validate Level 2 package

## Tech Stack

- **FastAPI** - Modern, fast web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

## Configuration

Configuration is managed via environment variables or `.env` file:

```bash
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
CORS_ORIGINS=["http://localhost:5173"]
```
