# 多平台视频源支持 / Multi-Platform Video Source Support

[English](#english) | 简体中文

---

## 简体中文

OpenFang Auto Clip 支持从多个视频平台下载和处理视频。

### 支持的平台

| 平台 | 状态 | 说明 |
|------|------|------|
| **YouTube** | ✅ 完全支持 | 包括 youtube.com 和 youtu.be 短链接 |
| **Bilibili** | ✅ 支持 | 需要网络环境支持 |
| **抖音 (Douyin)** | ✅ 支持 | 中国版 TikTok |
| **本地文件** | ✅ 支持 | 支持 mp4, avi, mov, mkv 等格式 |
| **直链 URL** | ✅ 支持 | 直接指向视频文件的 URL |
| **通用** | ✅ 支持 | 使用 yt-dlp 自动检测其他平台 |

### 使用方法

#### YouTube

```bash
# 标准 URL
python3 auto_clip.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 短链接
python3 auto_clip.py "https://youtu.be/dQw4w9WgXcQ"
```

#### Bilibili

```bash
# BV 号
python3 auto_clip.py "https://www.bilibili.com/video/BV1xx411c7mD"

# AV 号
python3 auto_clip.py "https://www.bilibili.com/video/av12345678"
```

#### 抖音 (Douyin)

```bash
python3 auto_clip.py "https://www.douyin.com/video/123456789"
```

#### 本地文件

```bash
# 相对路径
python3 auto_clip.py "./videos/my_video.mp4"

# 绝对路径
python3 auto_clip.py "/path/to/video.mp4"

# file:// URL
python3 auto_clip.py "file:///path/to/video.mp4"
```

#### 直链 URL

```bash
# 任何直接指向视频文件的 URL
python3 auto_clip.py "https://example.com/videos/sample.mp4"
```

#### 通用平台

对于任何其他支持 yt-dlp 的平台：

```bash
python3 auto_clip.py "https://[any-supported-platform].com/video_id"
```

### 批量处理不同平台

```bash
# 创建批量文件
cat > urls.txt << EOF
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.bilibili.com/video/BV1xx411c7mD
./videos/local_video.mp4
https://www.douyin.com/video/123456789
EOF

# 运行批量处理
python3 auto_clip.py --batch-file urls.txt
```

### 配置选项

某些平台可能需要额外配置：

#### Cookie 配置

某些平台（如 Bilibili、抖音）可能需要登录 Cookie：

```bash
# 使用浏览器导出的 Cookie 文件
yt-dlp --cookies cookies.txt "URL"

# 或在配置文件中设置
echo "cookie_file = /path/to/cookies.txt" >> ~/.openfang/auto_clip_config.json
```

#### 代理设置

```bash
# 使用环境变量
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

python3 auto_clip.py "URL"
```

### 故障排查

#### Bilibili 下载失败

```
错误: Bilibili download failed
解决:
1. 检查网络环境
2. 使用 Cookie 文件
3. 配置代理
```

#### 抖音下载失败

```
错误: Douyin download failed
解决:
1. 添加 --no-check-certificate 参数
2. 使用 Cookie 文件
3. 检查 URL 是否有效
```

#### 本地文件不支持

```
错误: Unsupported video format
解决: 确保文件是常见视频格式 (mp4, avi, mov, mkv, flv, wmv, webm)
```

### 开发者信息

添加新的视频平台支持：

1. 在 `src/video_sources.py` 中创建新的 `VideoSource` 子类
2. 实现 `validate()`, `extract_info()`, `download()` 方法
3. 在 `get_video_source()` 函数中添加平台检测
4. 更新本文档

---

## English

OpenFang Auto Clip supports downloading and processing videos from multiple platforms.

### Supported Platforms

| Platform | Status | Notes |
|----------|--------|-------|
| **YouTube** | ✅ Fully Supported | Including youtube.com and youtu.be short links |
| **Bilibili** | ✅ Supported | Requires appropriate network environment |
| **Douyin** | ✅ Supported | Chinese version of TikTok |
| **Local Files** | ✅ Supported | Supports mp4, avi, mov, mkv formats |
| **Direct URLs** | ✅ Supported | Direct URLs to video files |
| **Generic** | ✅ Supported | Uses yt-dlp auto-detection for other platforms |

### Usage

#### YouTube

```bash
# Standard URL
python3 auto_clip.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Short link
python3 auto_clip.py "https://youtu.be/dQw4w9WgXcQ"
```

#### Bilibili

```bash
# BV ID
python3 auto_clip.py "https://www.bilibili.com/video/BV1xx411c7mD"

# AV ID
python3 auto_clip.py "https://www.bilibili.com/video/av12345678"
```

#### Douyin

```bash
python3 auto_clip.py "https://www.douyin.com/video/123456789"
```

#### Local Files

```bash
# Relative path
python3 auto_clip.py "./videos/my_video.mp4"

# Absolute path
python3 auto_clip.py "/path/to/video.mp4"

# file:// URL
python3 auto_clip.py "file:///path/to/video.mp4"
```

#### Direct URLs

```bash
# Any URL pointing directly to a video file
python3 auto_clip.py "https://example.com/videos/sample.mp4"
```

#### Generic Platforms

For any other yt-dlp supported platform:

```bash
python3 auto_clip.py "https://[any-supported-platform].com/video_id"
```

### Batch Processing Multiple Platforms

```bash
# Create batch file
cat > urls.txt << EOF
https://www.youtube.com/watch?v=VIDEO_ID1
https://www.bilibili.com/video/BV1xx411c7mD
./videos/local_video.mp4
https://www.douyin.com/video/123456789
EOF

# Run batch processing
python3 auto_clip.py --batch-file urls.txt
```

### Configuration Options

Some platforms may require additional configuration:

#### Cookie Configuration

Some platforms (Bilibili, Douyin) may require login cookies:

```bash
# Use browser-exported cookie file
yt-dlp --cookies cookies.txt "URL"

# Or set in config file
echo "cookie_file = /path/to/cookies.txt" >> ~/.openfang/auto_clip_config.json
```

#### Proxy Settings

```bash
# Use environment variables
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

python3 auto_clip.py "URL"
```

### Troubleshooting

#### Bilibili Download Failed

```
Error: Bilibili download failed
Solutions:
1. Check network environment
2. Use cookie file
3. Configure proxy
```

#### Douyin Download Failed

```
Error: Douyin download failed
Solutions:
1. Add --no-check-certificate flag
2. Use cookie file
3. Verify URL is valid
```

#### Local File Not Supported

```
Error: Unsupported video format
Solution: Ensure file is common video format (mp4, avi, mov, mkv, flv, wmv, webm)
```

### Developer Information

To add support for a new video platform:

1. Create a new `VideoSource` subclass in `src/video_sources.py`
2. Implement `validate()`, `extract_info()`, `download()` methods
3. Add platform detection in `get_video_source()` function
4. Update this documentation

### Platform-Specific Notes

#### YouTube
- No special configuration required
- Supports all video qualities
- Automatic subtitle download available

#### Bilibili
- May require cookies for some videos
- Region restrictions may apply
- Consider using a proxy if needed

#### Douyin
- Requires --no-check-certificate for some videos
- Cookies recommended for better success rate
- URL format may change, update if needed

#### Local Files
- Supports all FFmpeg-compatible formats
- No network required
- Faster processing (no download time)

### Performance Tips

1. **Local files** process fastest (no download time)
2. **Batch processing** works across all platforms
3. **Parallel workers** limited by download bandwidth
4. **Cache downloads** when reprocessing same videos
