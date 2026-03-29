# Testing Guide for OpenFang Auto Clip

## Quick Start

### Run All Tests

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=sdk --cov-report=html
```

### Run Specific Test Suites

```bash
# Run SDK tests only
pytest tests/test_sdk/

# Run API tests only
pytest tests/test_api/

# Run integration tests only
pytest tests/test_integration/

# Run a specific test file
pytest tests/test_sdk/test_client.py

# Run a specific test
pytest tests/test_sdk/test_client.py::TestClientInitialization::test_init_default
```

### Run with Options

```bash
# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Run with pdb debugger on failure
pytest --pdb

# Run last failed tests
pytest --lf

# Print slowest tests
pytest --durations=10
```

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── pytest.ini               # Pytest configuration
├── requirements.txt          # Test dependencies
├── test_api/                # API endpoint tests
│   └── test_endpoints.py
├── test_sdk/                # SDK client tests
│   └── test_client.py
├── test_integration/         # Integration tests
│   └── test_workflows.py
└── fixtures/                # Test fixtures and data
```

---

## Writing Tests

### SDK Tests

```python
from openfang_sdk import Client
from unittest.mock import patch

class TestMyFeature:
    def test_feature_success(self):
        with patch('openfang_sdk.client.httpx.Client') as mock_httpx:
            # Setup mock
            mock_response = Mock()
            mock_response.json.return_value = {"status": "ok"}

            mock_client = Mock()
            mock_client.request.return_value = mock_response
            mock_httpx.return_value = mock_client

            # Test
            client = Client()
            result = client.some_method()

            # Assert
            assert result["status"] == "ok"
```

### API Tests

```python
from fastapi.testclient import TestClient

def test_endpoint(api_client):
    response = api_client.get("/api/v1/endpoint")

    assert response.status_code == 200
    data = response.json()
    assert "key" in data
```

### Integration Tests

```python
@pytest.mark.integration
def test_workflow(sample_transcript):
    # Test complete workflow
    client = Client()
    job = client.process(level=2, transcript_path=str(sample_transcript))
    result = client.wait_for_job(job['job_id'])

    assert result["status"] == "completed"
```

---

## Fixtures

### Available Fixtures

- `temp_dir` - Temporary directory for tests
- `sample_transcript` - Sample SRT file
- `sample_package` - Sample Level 2 package
- `api_client` - Test API client
- `test_db` - Test database session
- `mock_api_response` - Mock API response data
- `mock_job_data` - Mock job data

### Using Fixtures

```python
def test_with_fixture(sample_transcript):
    # fixture is automatically available
    assert sample_transcript.exists()

    with open(sample_transcript) as f:
        content = f.read()
    assert len(content) > 0
```

---

## Coverage

### Generate Coverage Report

```bash
# HTML report
pytest --cov=api --cov=sdk --cov-report=html

# Terminal report
pytest --cov=api --cov=sdk --cov-report=term-missing

# Combined
pytest --cov=api --cov=sdk --cov-report=html --cov-report=term
```

### View Coverage Report

```bash
# Open HTML report in browser
open htmlcov/index.html

# Or
python -m http.server 8000 -d htmlcov
# Then visit http://localhost:8000
```

### Coverage Goals

- **Target:** 80%+ overall coverage
- **Critical paths:** 90%+ coverage
  - API endpoints
  - SDK client methods
  - Database operations

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r tests/requirements.txt

    - name: Run tests
      run: pytest --cov=api --cov=sdk --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Debugging Failed Tests

### Run with Verbose Output

```bash
pytest -v -s tests/test_sdk/test_client.py::TestClientInitialization::test_init_default
```

### Drop into PDB on Failure

```bash
pytest --pdb
```

### Run Last Failed Tests

```bash
pytest --lf
```

### Show Print Statements

```bash
pytest -s
```

---

## Best Practices

1. **Test Isolation** - Each test should be independent
2. **Descriptive Names** - Use clear test names
3. **Arrange-Act-Assert** - Structure tests clearly
4. **Mock External Dependencies** - Use mocks for APIs
5. **Use Fixtures** - Reuse test setup code
6. **Test Edge Cases** - Don't just test happy paths
7. **Keep Tests Fast** - Use mocks, avoid slow operations
8. **Maintain Tests** - Update tests when code changes

---

## Common Issues

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'api'`

**Solution:**
```bash
# Run from project root
cd /path/to/openfang-auto-clip
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Database Locks

**Problem:** Tests fail with database lock errors

**Solution:**
```python
# Use in-memory database for tests
engine = create_engine("sqlite:///:memory:")
```

### Async Tests

**Problem:** Async tests hang or fail

**Solution:**
```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Run with asyncio mode
pytest --asyncio-mode=auto
```

---

## Continuous Improvement

### Regular Tasks

- [ ] Add tests for new features
- [ ] Increase coverage percentage
- [ ] Fix flaky tests
- [ ] Update test documentation
- [ ] Review test reports

### Goals

- **Week 1:** Achieve 60% coverage
- **Week 2:** Achieve 75% coverage
- **Week 3:** Achieve 80%+ coverage
- **Ongoing:** Maintain 80%+ coverage

---

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [httpx Mocking](https://www.python-httpx.org/mock/)
- [Coverage.py](https://coverage.readthedocs.io/)
