# Docker 部署指南 / Docker Deployment Guide

[English](#english) | 简体中文

---

## 简体中文

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip

# 2. 使用 Docker Compose 启动
docker-compose up -d

# 3. 运行环境检查
docker-compose run openfang-auto-clip --doctor

# 4. 运行快速演示
docker-compose run openfang-auto-clip --quick-demo
```

### 常用命令

```bash
# 处理视频
docker-compose run openfang-auto-clip \
  python3 auto_clip.py "https://www.youtube.com/watch?v=VIDEO_ID" --transform 1

# 启动 Web 管理界面
docker-compose up openfang-auto-clip web

# 查看日志
docker-compose logs -f openfang-auto-clip

# 停止服务
docker-compose down

# 重新构建镜像
docker-compose build --no-cache
```

### 配置选项

在 `docker-compose.yml` 中配置：

```yaml
environment:
  # API 密钥（可选）
  - OPENAI_API_KEY=your_key_here
  - ANTHROPIC_API_KEY=your_key_here

  # 输出目录
  - OPENFANG_OUTPUT_DIR=/app/output

  # 配置目录
  - OPENFANG_CONFIG_DIR=/app/config
```

### 数据持久化

```yaml
volumes:
  # 输出文件（clips、downloads）
  - ./output:/app/output

  # 配置文件
  - ./config:/app/config

  # 输入视频
  - ./videos:/app/videos:ro
```

### 生产环境部署

```bash
# 使用生产配置
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 配置反向代理（Nginx）
# 访问: http://your-domain.com
```

---

## English

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/outhsics/openfang-auto-clip.git
cd openfang-auto-clip

# 2. Start with Docker Compose
docker-compose up -d

# 3. Run environment check
docker-compose run openfang-auto-clip --doctor

# 4. Run quick demo
docker-compose run openfang-auto-clip --quick-demo
```

### Common Commands

```bash
# Process a video
docker-compose run openfang-auto-clip \
  python3 auto_clip.py "https://www.youtube.com/watch?v=VIDEO_ID" --transform 1

# Start Web Manager
docker-compose up openfang-auto-clip web

# View logs
docker-compose logs -f openfang-auto-clip

# Stop services
docker-compose down

# Rebuild image
docker-compose build --no-cache
```

### Configuration Options

Configure in `docker-compose.yml`:

```yaml
environment:
  # API Keys (optional)
  - OPENAI_API_KEY=your_key_here
  - ANTHROPIC_API_KEY=your_key_here

  # Output directory
  - OPENFANG_OUTPUT_DIR=/app/output

  # Config directory
  - OPENFANG_CONFIG_DIR=/app/config
```

### Data Persistence

```yaml
volumes:
  # Output files (clips, downloads)
  - ./output:/app/output

  # Configuration files
  - ./config:/app/config

  # Input videos
  - ./videos:/app/videos:ro
```

### Production Deployment

```bash
# Use production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Configure reverse proxy (Nginx)
# Access: http://your-domain.com
```

### Troubleshooting

**Container won't start:**
```bash
# Check logs
docker-compose logs openfang-auto-clip

# Rebuild image
docker-compose build --no-cache
```

**Permission errors:**
```bash
# Fix permissions on host
sudo chown -R $USER:$USER output/ config/
```

**FFmpeg not found:**
```bash
# Rebuild image (FFmpeg is included in Dockerfile)
docker-compose build --no-cache
```

### Advanced Configuration

#### Custom Startup Script

Create `config/startup.sh`:
```bash
#!/bin/bash
# Custom initialization
echo "Running custom startup..."
python3 auto_clip.py --doctor
```

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENFANG_OUTPUT_DIR` | Output directory | `/app/output` |
| `OPENFANG_CONFIG_DIR` | Config directory | `/app/config` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `PYTHONUNBUFFERED` | Python output | `1` |

#### Volume Mounting

```yaml
volumes:
  # Output
  - /path/on/host/output:/app/output

  # Config
  - /path/on/host/config:/app/config

  # Videos (read-only)
  - /path/on/host/videos:/app/videos:ro
```

### Docker Compose Profiles

```bash
# Start core services only
docker-compose --profile core up -d

# Start with database
docker-compose --profile with-db up -d

# Start all services
docker-compose --profile all up -d
```

### Health Checks

```bash
# Check container health
docker-compose ps
docker inspect openfang-auto-clip | grep -A 10 Health

# Manual health check
docker-compose exec openfang-auto-clip python3 -c "import sys; sys.exit(0)"
```

### Performance Tuning

```yaml
services:
  openfang-auto-clip:
    # Add resource limits
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### Security Best Practices

1. **Use secrets for API keys:**
```yaml
secrets:
  openai_api_key:
    file: ./secrets/openai_api_key.txt
```

2. **Run as non-root user** (already configured in Dockerfile)

3. **Scan for vulnerabilities:**
```bash
docker scan openfang-auto-clip:latest
```

4. **Keep images updated:**
```bash
docker-compose pull
docker-compose up -d
```

### Support

For issues related to:
- **Docker deployment**: Check [GitHub Issues](https://github.com/outhsics/openfang-auto-clip/issues)
- **General usage**: See [DOCUMENTATION.md](DOCUMENTATION.md)
- **Security**: See [SECURITY.md](SECURITY.md)
