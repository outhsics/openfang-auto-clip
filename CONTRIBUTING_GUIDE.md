# 贡献指南 / Contributing Guide

[English](#english) | 简体中文

---

## 简体中文

感谢你对 OpenFang Auto Clip 的关注！我们欢迎各种形式的贡献。

### 🚀 快速开始

#### 1. Fork 并克隆仓库

```bash
# Fork 仓库后
git clone https://github.com/YOUR_USERNAME/openfang-auto-clip.git
cd openfang-auto-clip
```

#### 2. 设置开发环境

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖（包括开发依赖）
pip install -e .
pip install -r requirements-dev.txt  # 如果有的话
```

#### 3. 运行测试

```bash
# 运行所有测试
python3 -m unittest discover -s tests

# 运行特定测试
python3 tests/test_aigc_integration.py
```

#### 4. 代码风格

我们使用 Black 进行代码格式化：

```bash
pip install black
black src/ tests/
```

### 📋 贡献类型

#### Bug 修复

1. 在 Issues 中搜索相关问题
2. 如果没有，创建新 Issue 描述问题
3. Fork 仓库并创建分支：`git checkout -b fix/issue-number`
4. 修复 Bug 并添加测试
5. 提交 Pull Request

#### 新功能

1. 先在 Issues 中讨论你的想法
2. 获得反馈后创建分支：`git checkout -b feature/your-feature`
3. 实现功能并添加文档
4. 提交 Pull Request

#### 文档改进

1. 直接编辑文档文件
2. 创建分支：`git checkout -b docs/your-changes`
3. 提交 Pull Request

### 🎯 重点贡献领域

我们特别欢迎以下方面的贡献：

#### 高优先级

- **Level 2 成片重建**: 完善基于脚本包的视频重建
- **测试覆盖率**: 提高测试覆盖率，特别是新功能
- **性能优化**: 优化视频处理速度
- **文档改进**: 完善中英文文档

#### 中优先级

- **新 AIGC 提供商**: 集成更多 AI 服务
- **新的转换预设**: 添加更多风格预设
- **Web 界面改进**: 改进本地 Web 管理器
- **示例代码**: 添加更多使用示例

#### 低优先级

- **插件系统**: 设计并实现插件架构
- **移动端支持**: 移动应用或响应式界面
- **云端部署**: 可选的云端部署方案

### 📝 代码规范

#### Python 代码

- 遵循 PEP 8 规范
- 使用类型注解（Type Hints）
- 添加文档字符串（Docstrings）
- 保持函数简短（< 50 行）
- 使用有意义的变量名

#### 示例

```python
from typing import Dict, Optional, List

def process_video(
    input_path: str,
    output_path: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a video file with the given options.

    Args:
        input_path: Path to input video
        output_path: Path to output video
        options: Optional processing options

    Returns:
        Dictionary with processing results

    Raises:
        ValueError: If input file is invalid
        ProcessingError: If processing fails
    """
    # Implementation here
    pass
```

#### 文档

- 使用清晰的标题和章节
- 提供代码示例
- 中英文双语
- 更新相关的 CHANGELOG

### 🧪 测试指南

#### 单元测试

```python
import unittest
from src.my_module import my_function

class TestMyFunction(unittest.TestCase):
    """Test cases for my_function"""

    def test_basic_case(self):
        """Test with basic input"""
        result = my_function("test")
        self.assertEqual(result, "expected")

    def test_edge_case(self):
        """Test with edge case"""
        result = my_function("")
        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
```

#### 集成测试

对于需要外部依赖的测试，使用 mock：

```python
from unittest.mock import Mock, patch

def test_video_download():
    with patch('src.video_sources.yt_dlp') as mock_ytdlp:
        mock_ytdlp.YoutubeDL.return_value.download.return_value = True
        # Test code here
```

### 📂 项目结构

```
openfang-auto-clip/
├── src/                    # 源代码
│   ├── aigc/              # AIGC 集成
│   ├── agent_skills/      # Agent 技能系统
│   ├── video_sources.py   # 视频下载
│   └── transform_effects.py # 转换效果
├── tests/                 # 测试文件
├── docs/                  # 文档
├── examples/              # 示例代码
├── scripts/               # 辅助脚本
├── config/                # 配置文件
├── auto_clip.py          # 主入口
├── setup.py              # 安装配置
├── requirements.txt      # 依赖
├── README.md            # 项目说明
└── CHANGELOG.md         # 变更日志
```

### 🔄 Pull Request 流程

1. **更新分支**: 确保你的分支是最新的
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **运行测试**: 确保所有测试通过
   ```bash
   python3 -m unittest discover -s tests
   ```

3. **格式化代码**: 使用 Black 格式化
   ```bash
   black src/ tests/
   ```

4. **提交 PR**: 填写 PR 模板
   - 描述你的更改
   - 关联相关 Issue
   - 添加截图（如果适用）

5. **等待审查**: 维护者会审查你的 PR

6. **处理反馈**: 根据反馈进行修改

### 📌 PR 模板

```markdown
## 描述
简要描述这个 PR 的目的和更改内容。

## 类型
- [ ] Bug 修复
- [ ] 新功能
- [ ] 文档改进
- [ ] 重构
- [ ] 性能优化
- [ ] 其他

## 测试
描述你如何测试这些更改：
- [ ] 单元测试通过
- [ ] 手动测试
- [ ] 添加了新测试

## 检查清单
- [ ] 代码遵循项目规范
- [ ] 添加了必要的文档
- [ ] 更新了 CHANGELOG
- [ ] 所有测试通过

## 关联 Issue
Closes #issue_number
```

### 🎨 资源

#### 颜色和样式

- 主色调: #2563EB (蓝色)
- 成功: #10B981 (绿色)
- 错误: #EF4444 (红色)
- 警告: #F59E0B (黄色)

#### 文档资源

- [Python 文档](https://docs.python.org/)
- [FFmpeg 文档](https://ffmpeg.org/documentation.html)
- [Whisper 文档](https://github.com/openai/whisper)

### 💬 交流渠道

- **GitHub Issues**: 报告 Bug 和功能请求
- **GitHub Discussions**: 一般讨论和问题
- **Pull Requests**: 代码审查和贡献

### ⭐️ 成为维护者

活跃的贡献者可以成为项目维护者：

1. 持续贡献高质量代码
2. 审查其他人的 PR
3. 参与项目决策讨论
4. 帮助回答用户问题

---

## English

Thank you for your interest in OpenFang Auto Clip! We welcome all forms of contributions.

### 🚀 Quick Start

#### 1. Fork and Clone

```bash
# After forking
git clone https://github.com/YOUR_USERNAME/openfang-auto-clip.git
cd openfang-auto-clip
```

#### 2. Setup Development Environment

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .
```

#### 3. Run Tests

```bash
# Run all tests
python3 -m unittest discover -s tests

# Run specific test
python3 tests/test_aigc_integration.py
```

### 📋 Contribution Types

#### Bug Fixes

1. Search for related issues
2. Create new issue if needed
3. Create branch: `git checkout -b fix/issue-number`
4. Fix bug and add tests
5. Submit Pull Request

#### New Features

1. Discuss your idea in Issues first
2. Create branch: `git checkout -b feature/your-feature`
3. Implement with documentation
4. Submit Pull Request

### 🎯 Priority Areas

We especially welcome contributions in:

**High Priority:**
- Level 2 video rebuild
- Test coverage
- Performance optimization
- Documentation improvements

**Medium Priority:**
- New AIGC providers
- New transform presets
- Web UI improvements
- Example code

### 📝 Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Keep functions short (< 50 lines)
- Use meaningful variable names

### 🔄 Pull Request Process

1. Update your branch
2. Run tests
3. Format code with Black
4. Submit PR with template
5. Wait for review
6. Address feedback

### 💬 Communication

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General discussions
- **Pull Requests**: Code review and contributions

Thank you for contributing! 🎉
