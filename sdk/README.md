# OpenFang SDK - Python Client

Easy-to-use Python client for the OpenFang Auto Clip API.

## Installation

```bash
pip install openfang-sdk
```

Or install from source:

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip/sdk
pip install -e .
```

## Quick Start

```python
from openfang_sdk import Client

# Initialize client
client = Client(base_url="http://localhost:8000")

# Check API health
health = client.health_check()
print(f"API Status: {health['status']}")

# Process a transcript
job = client.process(
    level=2,
    transcript_path="transcript.srt",
    config={"content_type": "auto", "default_duration": 60}
)
print(f"Job ID: {job['job_id']}")

# Wait for completion
result = client.wait_for_job(job['job_id'])
print(f"Status: {result['status']}")
print(f"Result: {result['result']}")

# Validate package
validation = client.validate_package("output/package.json")
print(f"Quality Score: {validation['overall_score']}/10")
print(f"Grade: {validation['grade']}")
```

## Features

- ✅ Simple, intuitive API
- ✅ Type hints throughout
- ✅ Automatic retry logic
- ✅ Error handling with custom exceptions
- ✅ Context manager support
- ✅ Async-friendly design
- ✅ Comprehensive documentation

## API Reference

### Initialization

```python
from openfang_sdk import Client

client = Client(
    api_key="your-api-key",  # Optional for now
    base_url="http://localhost:8000",
    timeout=30.0,
    max_retries=3
)
```

### Methods

#### health_check()

Check API health status.

```python
health = client.health_check()
# Returns: {"status": "healthy", "version": "0.5.0"}
```

#### upload_file()

Upload a transcript file.

```python
info = client.upload_file("transcript.srt")
# Returns: {"file_id": "...", "path": "...", "size": 1234}
```

#### process()

Start processing a video/transcript.

```python
job = client.process(
    level=2,
    transcript_path="transcript.srt",
    config={"content_type": "auto", "default_duration": 60}
)
# Returns: {"job_id": "...", "status": "pending"}
```

#### list_jobs()

List all jobs with optional filtering.

```python
jobs = client.list_jobs(status="completed", limit=10)
```

#### get_job()

Get job details.

```python
job = client.get_job("job-id")
# Returns: {"id": "...", "status": "completed", ...}
```

#### delete_job()

Delete/cancel a job.

```python
client.delete_job("job-id")
```

#### wait_for_job()

Wait for a job to complete.

```python
result = client.wait_for_job("job-id", check_interval=2.0, timeout=300)
```

#### validate_package()

Validate a Level 2 package.

```python
result = client.validate_package(
    "package.json",
    original_transcript="Original transcript..."
)
# Returns: {"overall_score": 9.5, "grade": "A", ...}
```

## Context Manager

Use as a context manager for automatic cleanup:

```python
from openfang_sdk import Client

with Client() as client:
    job = client.process(level=2, transcript_path="transcript.srt")
    result = client.wait_for_job(job['job_id'])
# Client automatically closed
```

## Error Handling

The SDK provides specific exceptions for different error types:

```python
from openfang_sdk import Client
from openfang_sdk import (
    APIError,
    ValidationError,
    UploadError,
    JobNotFoundError,
    ProcessingError
)

try:
    job = client.process(level=2, transcript_path="transcript.srt")
    result = client.wait_for_job(job['job_id'])

except ValidationError as e:
    print(f"Validation error: {e.message}")

except JobNotFoundError as e:
    print(f"Job not found: {e.job_id}")

except ProcessingError as e:
    print(f"Processing failed: {e.message}")

except APIError as e:
    print(f"API error: {e.message}")
```

## Examples

### Example 1: Process and Validate

```python
from openfang_sdk import Client

with Client() as client:
    # Upload transcript
    upload_info = client.upload_file("transcript.srt")

    # Start processing
    job = client.process(
        level=2,
        uploaded_file_id=upload_info['file_id'],
        config={"content_type": "educational"}
    )

    # Wait for completion
    result = client.wait_for_job(job['job_id'])

    # Validate result
    if result['status'] == 'completed':
        validation = client.validate_package(result['result']['output_path'])
        print(f"Quality: {validation['overall_score']}/10 ({validation['grade']})")
```

### Example 2: Batch Processing

```python
from openfang_sdk import Client

transcripts = ["video1.srt", "video2.srt", "video3.srt"]

with Client() as client:
    jobs = []

    # Start all jobs
    for transcript in transcripts:
        job = client.process(level=2, transcript_path=transcript)
        jobs.append(job['job_id'])

    # Wait for all to complete
    results = []
    for job_id in jobs:
        result = client.wait_for_job(job_id)
        results.append(result)

    print(f"Completed {len(results)} jobs")
```

### Example 3: Monitor Job Progress

```python
from openfang_sdk import Client
import time

with Client() as client:
    job = client.process(level=2, transcript_path="transcript.srt")

    # Monitor progress
    while True:
        job_info = client.get_job(job['job_id'])

        print(f"Status: {job_info['status']}, Progress: {job_info['progress']}%")

        if job_info['status'] in ['completed', 'failed']:
            break

        time.sleep(2)
```

## Development

### Install from source

```bash
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip/sdk
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=openfang_sdk --cov-report=html
```

## License

MIT License - See [LICENSE](https://github.com/outhsics/openfang-auto-clip/blob/main/LICENSE) for details.

## Support

- **Documentation**: https://github.com/outhsics/openfang-auto-clip
- **Issues**: https://github.com/outhsics/openfang-auto-clip/issues
- **Discussions**: https://github.com/outhsics/openfang-auto-clip/discussions
