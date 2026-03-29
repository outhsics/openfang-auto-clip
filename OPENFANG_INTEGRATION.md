# OpenFang Integration

OpenFang Auto Clip integrates with [OpenFang](https://github.com/RightNow-AI/openfang) (⭐ 15,000+ stars), the open-source Agent Operating System.

## What You Get

- **AI Moment Detection**: Automatically finds best moments
- **8-Phase Pipeline**: Battle-tested video processing
- **Rust Performance**: 40MB memory, 180ms cold start
- **1,767+ Tests**: Production-ready reliability

## Installation

```bash
# Install OpenFang
curl -fsSL https://openfang.sh/install | sh

# Initialize
openfang init

# Activate Clip Hand
openfang hand activate clip
```

## Usage

```python
from openfang_wrapper import OpenFangWrapper

wrapper = OpenFangWrapper()
result = wrapper.process_video(
    "https://youtube.com/watch?v=dQw4w9WgXcQ",
    output_dir="./clips"
)
```

## Architecture

```
openfang-auto-clip (Python UI)
    ↓ subprocess
OpenFang (Rust Engine)
    └── Clip Hand (8-phase pipeline)
```

## Benefits

| Feature | OpenFang Auto Clip | Traditional Tools |
|---------|-------------------|-------------------|
| Cold Start | 180ms | 2-4s |
| Memory | 40MB | 180-250MB |
| Install Size | 32MB | 100-200MB |
| AI Detection | ✅ Included | ❌ Manual |
| Tests | 1,767+ | Variable |

## Links

- [OpenFang GitHub](https://github.com/RightNow-AI/openfang)
- [Documentation](https://openfang.sh/docs)
- [Install Guide](https://openfang.sh/docs/getting-started)
