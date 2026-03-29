# Contributing to OpenFang Auto Clip

感谢您对 OpenFang Auto Clip 项目的关注！我们欢迎各种形式的贡献。

---

## 🚀 Quick Start

### For First-Time Contributors

1. **Fork the repository**
   ```bash
   # Click "Fork" button on GitHub
   git clone https://github.com/YOUR_USERNAME/openfang-auto-clip.git
   cd openfang-auto-clip
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Run tests**
   ```bash
   pytest
   ```

4. **Make your changes**
   - Create a new branch: `git checkout -b feature/your-feature`
   - Make your changes
   - Commit: `git commit -m "feat: add your feature"`
   - Push: `git push origin feature/your-feature`

5. **Create Pull Request**
   - Go to GitHub and click "New Pull Request"
   - Fill in the PR template
   - Wait for review

---

## 📋 Development Setup

### Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18+ (for web dashboard)
- **FFmpeg**: For video processing
- **Git**: For version control

### Environment Setup

```bash
# 1. Clone your fork
git clone https://github.com/YOUR_USERNAME/openfang-auto-clip.git
cd openfang-auto-clip

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Set up pre-commit environment
pre-commit install-hooks
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov=sdk --cov-report=html

# Run specific test file
pytest tests/test_sdk/test_client.py

# Run with verbose output
pytest -v

# Run only fast tests
pytest -m "not slow"
```

### Running the Application

```bash
# Start API server
cd api
python -m uvicorn main:app --reload --port 8000

# Start web dashboard (new terminal)
cd web
npm install
npm run dev
```

The web dashboard will be available at `http://localhost:5173`

---

## 🎨 Code Style Guide

### Python Code Style

We follow **PEP 8** with some modifications:

#### Formatting

```python
# ✅ Good - Clear naming
def process_transcript(transcript_path: str, level: int = 2) -> dict:
    """Process transcript and generate package.

    Args:
        transcript_path: Path to transcript file
        level: Transformation level (1, 2, or 3)

    Returns:
        Generated package dictionary
    """
    # Implementation...

# ❌ Bad - Unclear naming
def proc(tp, l=2):
    # Implementation...
```

#### Type Hints

```python
# ✅ Good - Complete type hints
from typing import Optional, Dict, List

def generate_package(
    content: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Generate Level 2 package."""
    pass

# ❌ Bad - Missing type hints
def generate_package(content, config=None):
    pass
```

#### Documentation

```python
# ✅ Good - Complete docstring
def validate_package(package: Dict[str, Any]) -> ValidationResult:
    """Validate Level 2 package quality.

    Performs comprehensive validation including:
    - Content coherence analysis
    - Quality scoring
    - Copyright risk assessment

    Args:
        package: Package dictionary to validate

    Returns:
        ValidationResult with scores and recommendations

    Raises:
        ValidationError: If package structure is invalid

    Examples:
        >>> result = validate_package(package)
        >>> print(result.overall_score)
        8.5
    """
    pass
```

### JavaScript/Vue Code Style

We use **ESLint** and **Prettier** for consistent formatting:

```javascript
// ✅ Good - Clear component structure
<template>
  <div class="process-form">
    <el-form @submit="handleSubmit">
      <!-- Form content -->
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { processVideo } from '@/api'

const form = ref({
  level: 2,
  duration: 60
})

const handleSubmit = async () => {
  try {
    await processVideo(form.value)
  } catch (error) {
    console.error('Processing failed:', error)
  }
}
</script>

// ❌ Bad - Mixed concerns, unclear structure
```

### Commit Message Style

We follow **Conventional Commits**:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

#### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Test additions/changes
- `chore`: Build process or auxiliary tool changes

#### Examples

```bash
# Feature
git commit -m "feat(api): add authentication endpoint"

# Bug fix
git commit -m "fix(web): resolve file upload progress display"

# Documentation
git commit -m "docs: update API documentation with examples"

# Refactoring
git commit -m "refactor(sdk): simplify error handling with custom exceptions"
```

---

## 🔄 Pull Request Workflow

### Before Creating PR

1. **Update your branch**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests**
   ```bash
   pytest
   pytest --cov
   ```

3. **Run linters**
   ```bash
   # Python
   black .
   isort .
   flake8

   # JavaScript
   cd web
   npm run lint
   npm run format
   ```

4. **Update documentation**
   - Update README if needed
   - Add docstrings to new functions
   - Update API docs

### Creating PR

1. **Push your changes**
   ```bash
   git push origin feature/your-feature
   ```

2. **Create Pull Request on GitHub**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill in the PR template

3. **PR Template**

   ```markdown
   ## Description
   Brief description of changes...

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Tests added/updated
   - [ ] All tests pass
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guide
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No new warnings generated

   ## Related Issues
   Closes #123
   ```

### After Creating PR

1. **Wait for CI checks to pass**
   - All tests must pass
   - Code coverage must not decrease
   - Linters must pass

2. **Address review comments**
   - Respond to all comments
   - Make requested changes
   - Push updates to your branch

3. **Approval and merge**
   - At least one maintainer approval required
   - CI must be green
   - No merge conflicts

---

## 🐛 Bug Reports

### Before Reporting

1. **Search existing issues**
   - Check if bug is already reported
   - Add details to existing issue if found

2. **Gather information**
   - Python version
   - OpenFang Auto Clip version
   - Operating system
   - Error messages
   - Steps to reproduce

### Bug Report Template

```markdown
## Bug Description
Clear description of the bug...

## Environment
- Python version: 3.10.5
- OpenFang version: 0.5.0
- OS: Ubuntu 22.04

## Steps to Reproduce
1. Step one...
2. Step two...
3. Step three...

## Expected Behavior
What should happen...

## Actual Behavior
What actually happens...

## Error Messages
```
Error traceback...
```

## Additional Context
Screenshots, logs, or other relevant information...
```

---

## 💡 Feature Requests

### Before Requesting

1. **Check if feature exists**
   - Read documentation
   - Search issues
   - Check roadmap

2. **Think about use case**
   - What problem does it solve?
   - Who would benefit?
   - Is it general-purpose or specific?

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature...

## Problem Statement
What problem does this solve?

## Proposed Solution
How should it work?

## Alternatives Considered
What other approaches did you consider?

## Additional Context
Examples, mockups, or references...
```

---

## 🎯 Areas to Contribute

### Good First Issues

Look for issues labeled `good first issue`:
- Documentation improvements
- Simple bug fixes
- Test additions
- UI improvements

### High Priority Areas

1. **Testing**
   - Increase test coverage
   - Add integration tests
   - Improve test reliability

2. **Documentation**
   - Add more examples
   - Improve API docs
   - Create tutorials

3. **Web Dashboard**
   - UI/UX improvements
   - New features
   - Performance optimization

4. **Level 1 & Level 3**
   - Implement Level 1 (basic processing)
   - Implement Level 3 (advanced processing)

5. **Community**
   - Template gallery
   - Success stories
   - Video tutorials

---

## 📜 Code of Conduct

### Our Pledge

We are committed to making participation in our project a harassment-free experience.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior includes:**
- Harassment, trolling, or derogatory comments
- Personal or political attacks
- Public or private harassment
- Publishing private information

### Enforcement

Project maintainers may remove/edit comments or ban contributors who do not follow this code of conduct.

---

## 🏆 Recognition

### Contributors Hall of Fame

All contributors are recognized in:
- README.md contributors section
- Release notes
- Annual community posts

### Top Contributors

Special recognition for:
- Most PRs merged
- Most issues resolved
- Most valuable contributions
- Long-term support

---

## 📚 Additional Resources

### Documentation

- [README](README.md) - Project overview
- [API Docs](api/API_DOCS.md) - API reference
- [SDK Docs](sdk/README.md) - SDK guide
- [Testing Guide](tests/README.md) - Testing instructions

### Communication

- **Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **PRs**: Code contributions

### Learning Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Vue.js Docs](https://vuejs.org/)
- [pytest Docs](https://docs.pytest.org/)

---

## ❓ Questions?

### Getting Help

1. **Check documentation** - Most questions are answered there
2. **Search issues** - Similar questions may have been asked
3. **Create discussion** - For general questions
4. **Open issue** - For bugs or feature requests

### Contact Maintainers

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions
- **Email**: For private matters (if needed)

---

## 🙏 Thank You!

Every contribution, no matter how small, helps make OpenFang Auto Clip better!

**Together, we're building the best open-source video automation platform!** 🚀

---

**Last Updated**: 2026-03-29
**Version**: 0.5.0
