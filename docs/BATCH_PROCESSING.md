# 批量处理指南 / Batch Processing Guide

[English](#english) | 简体中文

---

## 简体中文

### 快速开始

```bash
# 1. 创建批量文件（支持 txt、csv、json）
echo "https://www.youtube.com/watch?v=VIDEO_ID1" > urls.txt
echo "https://www.youtube.com/watch?v=VIDEO_ID2" >> urls.txt

# 2. 运行批量处理
python3 auto_clip.py --batch-file urls.txt

# 3. 并行处理（4 个任务同时运行）
python3 auto_clip.py --batch-file urls.txt --parallel 4

# 4. 指定转换级别和时长
python3 auto_clip.py --batch-file urls.txt --transform 2 --duration 90
```

### 支持的文件格式

#### 1. 纯文本 (TXT)

一行一个 URL：

```
# 注释行会被忽略
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
https://www.youtube.com/watch?v=kJQP7kiw5Fk
```

#### 2. CSV 格式

```csv
url,transform,duration,transcript
https://www.youtube.com/watch?v=dQw4w9WgXcQ,1,60,
https://www.youtube.com/watch?v=9bZkp7q19f0,2,90,/path/to/transcript.srt
https://www.youtube.com/watch?v=kJQP7kiw5Fk,1,45,
```

#### 3. JSON 格式

```json
{
  "tasks": [
    {
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "transform_level": 1,
      "duration": 60
    },
    {
      "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
      "transform_level": 2,
      "duration": 90,
      "transcript_path": "/path/to/transcript.srt"
    }
  ]
}
```

### 高级功能

#### 断点续传

如果批量处理被中断，可以从指定 URL 恢复：

```bash
python3 auto_clip.py --batch-file urls.txt --resume-from "https://..."
```

#### 自定义配置

```bash
python3 auto_clip.py --batch-file urls.json \
  --transform 2 \
  --duration 90 \
  --parallel 4
```

### 输出目录

批量处理的结果保存在：

```
~/.openfang/clips/batches/TIMESTAMP/
├── batch_report.json    # 批量处理报告
└── resume.json          # 断点续传信息
```

### 报告格式

```json
{
  "batch_id": "20240324_123456",
  "batch_dir": "/path/to/batch/dir",
  "total_tasks": 10,
  "started_at": "2024-03-24T12:34:56",
  "completed_at": "2024-03-24T14:56:78",
  "summary": {
    "success": 8,
    "failed": 1,
    "skipped": 1
  },
  "tasks": [...]
}
```

---

## English

### Quick Start

```bash
# 1. Create batch file (txt, csv, json supported)
echo "https://www.youtube.com/watch?v=VIDEO_ID1" > urls.txt
echo "https://www.youtube.com/watch?v=VIDEO_ID2" >> urls.txt

# 2. Run batch processing
python3 auto_clip.py --batch-file urls.txt

# 3. Parallel processing (4 tasks at once)
python3 auto_clip.py --batch-file urls.txt --parallel 4

# 4. Specify transform level and duration
python3 auto_clip.py --batch-file urls.txt --transform 2 --duration 90
```

### Supported File Formats

#### 1. Plain Text (TXT)

One URL per line:

```
# Comment lines are ignored
https://www.youtube.com/watch?v=dQw4w9WgXcQ
https://www.youtube.com/watch?v=9bZkp7q19f0
https://www.youtube.com/watch?v=kJQP7kiw5Fk
```

#### 2. CSV Format

```csv
url,transform,duration,transcript
https://www.youtube.com/watch?v=dQw4w9WgXcQ,1,60,
https://www.youtube.com/watch?v=9bZkp7q19f0,2,90,/path/to/transcript.srt
https://www.youtube.com/watch?v=kJQP7kiw5Fk,1,45,
```

#### 3. JSON Format

```json
{
  "tasks": [
    {
      "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "transform_level": 1,
      "duration": 60
    },
    {
      "url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
      "transform_level": 2,
      "duration": 90,
      "transcript_path": "/path/to/transcript.srt"
    }
  ]
}
```

### Advanced Features

#### Resume from Interrupt

Resume batch processing from a specific URL:

```bash
python3 auto_clip.py --batch-file urls.txt --resume-from "https://..."
```

#### Custom Configuration

```bash
python3 auto_clip.py --batch-file urls.json \
  --transform 2 \
  --duration 90 \
  --parallel 4
```

### Output Directory

Batch processing results are saved to:

```
~/.openfang/clips/batches/TIMESTAMP/
├── batch_report.json    # Batch processing report
└── resume.json          # Resume information
```

### Report Format

```json
{
  "batch_id": "20240324_123456",
  "batch_dir": "/path/to/batch/dir",
  "total_tasks": 10,
  "started_at": "2024-03-24T12:34:56",
  "completed_at": "2024-03-24T14:56:78",
  "summary": {
    "success": 8,
    "failed": 1,
    "skipped": 1
  },
  "tasks": [...]
}
```

### Performance Tips

1. **Parallel Processing**: Use `--parallel 4` to process 4 videos simultaneously
2. **Resource Management**: Adjust parallel workers based on your CPU cores
3. **Network Bandwidth**: Download speeds may bottleneck parallel processing
4. **Disk Space**: Ensure sufficient space for all output files

### Error Handling

- Failed tasks are logged in the batch report
- Processing continues even if individual tasks fail
- Check `batch_report.json` for detailed error messages

### Examples

See `examples/batch/` directory for sample batch files:
- `urls.txt` - Plain text example
- `urls.csv` - CSV format example
- `urls.json` - JSON format example
