# OpenFang Auto Clip API - v0.5.0 Documentation

## Quick Start

### Installation

```bash
# Install dependencies
cd api
pip install -r requirements.txt

# Start API server
python -m api.main
```

The API will be available at http://localhost:8000

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## API Endpoints

### Health Check

Check if the API is running.

```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.5.0",
  "service": "openfang-api"
}
```

---

### File Upload

Upload a transcript file for processing.

```http
POST /api/v1/upload
Content-Type: multipart/form-data
```

**Parameters:**
- `file` - Transcript file (SRT, VTT, or TXT)
- Max size: 100MB

**Response:**
```json
{
  "file_id": "uuid-string",
  "filename": "transcript.srt",
  "path": "/path/to/uploaded/file",
  "size": 1234,
  "uploaded_at": "2026-03-29T12:00:00"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -F "file=@transcript.srt"
```

---

### Process Video/Transcript

Start a processing job.

```http
POST /api/v1/process
Content-Type: application/json
```

**Request Body:**
```json
{
  "level": 2,
  "transcript_path": "/path/to/transcript.srt",
  "uploaded_file_id": "uuid-from-upload",
  "video_url": "https://youtube.com/watch?v=...",
  "config": {
    "content_type": "auto",
    "default_duration": 60
  }
}
```

**Parameters:**
- `level` (required) - Transformation level (1, 2, or 3)
- One of:
  - `transcript_path` - Path to local transcript file
  - `uploaded_file_id` - ID from upload endpoint
  - `video_url` - URL to video
- `config` (optional) - Processing configuration

**Response:**
```json
{
  "job_id": "uuid-string",
  "status": "pending",
  "message": "Job created successfully",
  "created_at": "2026-03-29T12:00:00"
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{
    "level": 2,
    "uploaded_file_id": "abc123",
    "config": {
      "content_type": "auto",
      "default_duration": 60
    }
  }'
```

---

### List Jobs

Get all jobs with optional filtering.

```http
GET /api/v1/jobs?status=completed&limit=10
```

**Query Parameters:**
- `status` (optional) - Filter by status (pending, processing, completed, failed)
- `limit` (optional) - Maximum results (default: 50)

**Response:**
```json
[
  {
    "id": "job-uuid",
    "status": "completed",
    "level": 2,
    "progress": 100.0,
    "created_at": "2026-03-29T12:00:00",
    "updated_at": "2026-03-29T12:01:00",
    "result": {
      "level": 2,
      "output_path": "/path/to/package.json"
    }
  }
]
```

---

### Get Job Details

Get details of a specific job.

```http
GET /api/v1/jobs/{job_id}
```

**Response:**
```json
{
  "id": "job-uuid",
  "status": "processing",
  "level": 2,
  "progress": 50.0,
  "created_at": "2026-03-29T12:00:00",
  "updated_at": "2026-03-29T12:00:30",
  "result": null,
  "error": null
}
```

---

### Delete Job

Cancel or delete a job.

```http
DELETE /api/v1/jobs/{job_id}
```

**Response:** 204 No Content

---

### Validate Package

Validate a Level 2 package.

```http
POST /api/v1/validate
Content-Type: application/json
```

**Request Body:**
```json
{
  "package_path": "/path/to/package.json",
  "original_transcript": "Original transcript text..."
}
```

**Response:**
```json
{
  "overall_score": 9.5,
  "grade": "A",
  "scores": {
    "coherence": 9.8,
    "actionability": 9.5,
    "originality": 8.5,
    "value_retention": 9.2
  },
  "copyright_risk": {
    "risk_level": "Safe",
    "semantic_similarity": 0.15,
    "word_overlap": 0.08
  },
  "production_ready": true,
  "issues": [],
  "recommendations": []
}
```

---

## Job Status

Jobs progress through these statuses:

1. **pending** - Job created, waiting to start
2. **processing** - Currently processing (progress: 0-100%)
3. **completed** - Successfully completed
4. **failed** - Failed with error

## Processing Levels

### Level 1: Visual Remix
- Style transfer
- Speed adjustments
- Visual effects

### Level 2: Script Generation
- AI-powered short-form script
- Content-aware generation
- Visual direction
- Quality: 9.62/10

### Level 3: Complete Recreation
- Full recreation (coming soon)

## Configuration Options

### Content Types

- `auto` - Auto-detect content type
- `educational` - Educational content
- `entertainment` - Entertainment content
- `tutorial` - Tutorial content
- `general` - General content

### Duration

Target duration in seconds (30-300):
```json
{
  "default_duration": 60
}
```

### Output Formats

```json
{
  "output_formats": ["json", "srt", "md"]
}
```

---

## Error Responses

Errors follow this format:

```json
{
  "detail": "Error message"
}
```

**Status Codes:**
- 400 - Bad Request (invalid parameters)
- 404 - Not Found (job/file not found)
- 413 - Payload Too Large (file > 100MB)
- 429 - Rate Limit Exceeded
- 500 - Internal Server Error

---

## Python SDK Usage

```python
from openfang_sdk import Client

# Initialize
client = Client(base_url="http://localhost:8000")

# Process
job = client.process(
    level=2,
    transcript_path="transcript.srt",
    config={"content_type": "auto"}
)

# Wait for completion
result = client.wait_for_job(job['job_id'])

# Validate
validation = client.validate_package(result['result']['output_path'])
print(f"Quality: {validation['overall_score']}/10")
```

---

## Rate Limiting

Currently no rate limiting enforced.

Future: 60 requests/minute per API key.

---

## Database

Jobs are persisted in SQLite database at:
```
~/.openfang/data/openfang.db
```

Jobs persist across server restarts.

---

## Development

### Run with auto-reload:

```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### View SQL queries:

Set `DEBUG=true` in environment or api/config.py

---

## Deployment

### Docker

```bash
docker build -f Dockerfile.api -t openfang-api .
docker run -p 8000:8000 -v ~/.openfang:/root/.openfang openfang-api
```

### Docker Compose

```bash
docker-compose up api
```

---

## Support

- **Issues**: https://github.com/outhsics/openfang-auto-clip/issues
- **Discussions**: https://github.com/outhsics/openfang-auto-clip/discussions
- **Documentation**: https://github.com/outhsics/openfang-auto-clip
