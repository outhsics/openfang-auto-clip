# Agent Skills System / Agent 技能系统

[English](#english) | 简体中文

---

## 简体中文

OpenFang Auto Clip 包含一个完整的 Agent 技能系统，兼容 OpenClaw 框架，用于自动化视频处理任务。

### 核心特性

- **技能框架**: 可扩展的技能系统，支持自定义技能
- **工作流**: 将多个技能组合成复杂的工作流
- **上下文管理**: 跨技能共享变量和状态
- **执行器**: 高性能执行引擎，支持并行和错误处理
- **Agent**: 封装技能和工作流的智能代理

### 可用技能

| 技能 | 描述 | 参数 |
|------|------|------|
| `video_download` | 从 URL 下载视频 | url, output_dir, quality |
| `video_transform` | 应用版权保护转换 | input_path, preset, transform_level |
| `batch_process` | 批量处理多个视频 | urls, transform_level, parallel |
| `aigc_image` | 生成 AI 图像 | prompt, provider, style, variations |
| `aigc_video` | 生成 AI 视频 | prompt, provider, duration |
| `transcript_generate` | 生成视频字幕 | video_path, model, output_format |
| `clip_extract` | 从视频中提取片段 | input_path, segments, output_dir |

### 快速开始

#### Python API

**基础技能执行**

```python
from src.agent_skills import SkillExecutor

# 创建执行器
executor = SkillExecutor()

# 执行单个技能
result = executor.execute(
    skill_name="video_download",
    params={
        "url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "output_dir": "./downloads"
    }
)

if result.success:
    print(f"视频已下载: {result.data['video_path']}")
```

**使用 Agent**

```python
from src.agent_skills import Agent, create_video_processing_workflow

# 创建 Agent
agent = Agent(
    name="video_agent",
    description="视频处理专用 Agent"
)

# 添加技能
agent.add_skill("video_download")
agent.add_skill("video_transform")
agent.add_skill("clip_extract")

# 添加工作流
agent.add_workflow(create_video_processing_workflow())

# 执行任务
result = agent.execute(
    task="video_processing",
    params={
        "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "clip_segments": [(0, 30), (60, 90), (120, 150)]
    }
)
```

**创建自定义工作流**

```python
from src.agent_skills import Workflow, WorkflowExecutor

# 创建工作流
workflow = Workflow(
    name="my_workflow",
    description="我的自定义工作流"
)

# 添加步骤
workflow.add_step("video_download", {
    "url": "$video_url"
})

workflow.add_step("video_transform", {
    "input_path": "$video_download_result.video_path",
    "preset": "cinematic"
})

workflow.add_step("aigc_image", {
    "prompt": "电影级缩略图",
    "style": "cinematic"
})

# 保存工作流
workflow.save(Path("my_workflow.json"))

# 执行工作流
executor = WorkflowExecutor()
executor.load_workflow(Path("my_workflow.json"))

results = executor.execute_workflow(
    workflow_name="my_workflow",
    variables={"video_url": "https://..."}
)
```

**创建自定义技能**

```python
from src.agent_skills import Skill, SkillContext, SkillResult, SkillStatus, register_skill

@register_skill
class MyCustomSkill(Skill):
    """自定义技能示例"""

    name = "my_custom_skill"
    description = "这是一个自定义技能"
    version = "1.0.0"
    author = "Your Name"

    parameters = {
        "input": {
            "type": str,
            "description": "输入参数",
            "required": True
        },
        "option": {
            "type": str,
            "description": "可选参数",
            "required": False
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        input_value = kwargs.get("input")
        option = kwargs.get("option", "default")

        try:
            # 你的处理逻辑
            result = f"处理结果: {input_value} ({option})"

            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={"result": result}
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )
```

### 预设工作流

#### video_processing

标准视频处理流程：下载 → 转换 → 提取片段

```python
agent.execute("video_processing", {
    "video_url": "https://...",
    "output_dir": "./output",
    "clip_segments": [(0, 30), (60, 90)]
})
```

#### aigc_content

AI 内容生成流程：生成图像 → 生成视频

```python
agent.execute("aigc_content", {
    "image_prompt": "赛博朋克城市",
    "image_style": "cyberpunk",
    "video_prompt": "云层流动"
})
```

#### full_pipeline

完整管道：下载 → 转换 → 字幕 → 片段

```python
agent.execute("full_pipeline", {
    "video_url": "https://...",
    "preset": "cinematic"
})
```

### 技能链

按顺序执行多个技能，前一个技能的结果可用于后续技能：

```python
executor = SkillExecutor()

results = executor.execute_chain([
    {
        "skill": "video_download",
        "params": {"url": "https://..."}
    },
    {
        "skill": "video_transform",
        "params": {
            "input_path": "$video_download_result.video_path"
        }
    },
    {
        "skill": "clip_extract",
        "params": {
            "input_path": "$video_transform_result.output_path",
            "segments": [(0, 30), (60, 90)]
        }
    }
])
```

### 上下文和变量

在技能之间共享数据：

```python
executor = SkillExecutor()

# 设置变量
executor.context.set_var("api_key", "your-key")
executor.context.set_var("output_format", "mp4")

# 在技能中使用
result = executor.execute("my_skill", {
    "key": "$api_key",  # 引用变量
    "format": "$output_format"
})

# 获取技能结果
if result.success:
    video_path = result.data["video_path"]
    executor.context.set_var("last_video", video_path)
```

### 错误处理

```python
# stop_on_error=True: 遇到错误停止（默认）
results = executor.execute_workflow(
    workflow_name="my_workflow",
    stop_on_error=True
)

# stop_on_error=False: 继续执行
results = executor.execute_workflow(
    workflow_name="my_workflow",
    stop_on_error=False
)

# 检查结果
for i, result in enumerate(results):
    if result.success:
        print(f"步骤 {i+1}: 成功")
    else:
        print(f"步骤 {i+1}: 失败 - {result.error}")
```

### 工作流格式

工作流可以保存为 JSON 文件：

```json
{
  "name": "my_workflow",
  "description": "我的自定义工作流",
  "variables": {
    "video_url": "",
    "output_dir": "./output"
  },
  "steps": [
    {
      "skill": "video_download",
      "params": {
        "url": "$video_url",
        "output_dir": "$output_dir"
      }
    },
    {
      "skill": "video_transform",
      "params": {
        "input_path": "$video_download_result.video_path",
        "preset": "cinematic"
      },
      "condition": "video_download_result.get('success', False)"
    }
  ]
}
```

### CLI 集成

```bash
# 列出所有可用技能
python3 auto_clip.py --list-skills

# 执行单个技能
python3 auto_clip.py --execute-skill video_download \
    --params '{"url": "https://...", "output_dir": "./downloads"}'

# 执行工作流
python3 auto_clip.py --execute-workflow video_processing \
    --variables '{"video_url": "https://...", "clip_segments": [[0,30]]}'

# 创建新 Agent
python3 auto_clip.py --create-agent my_agent \
    --skills video_download,video_transform \
    --workflow video_processing
```

### 最佳实践

1. **模块化设计**: 将复杂任务分解为多个小技能
2. **复用工作流**: 创建可重用的工作流模板
3. **错误处理**: 使用 stop_on_error=False 批量处理
4. **变量引用**: 使用 $variable_name 在技能间传递数据
5. **条件执行**: 使用 condition 参数控制步骤执行

### 示例项目

**视频下载并转换**

```python
from src.agent_skills import SkillExecutor

executor = SkillExecutor()

# 下载
download_result = executor.execute("video_download", {
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
})

# 转换
if download_result.success:
    transform_result = executor.execute("video_transform", {
        "input_path": download_result.data["video_path"],
        "preset": "cinematic"
    })

    print(f"转换后视频: {transform_result.data['output_path']}")
```

**批量处理并生成 AIGC 内容**

```python
from src.agent_skills import Agent

agent = Agent("content_creator")
agent.add_skill("batch_process")
agent.add_skill("aigc_image")

# 批量处理视频
batch_result = agent.execute("batch_process", {
    "urls": [
        "https://youtube.com/watch?v=1",
        "https://youtube.com/watch?v=2"
    ],
    "transform_level": 1
})

# 生成封面图
if batch_result.success:
    cover_result = agent.execute("aigc_image", {
        "prompt": "科技感缩略图",
        "style": "cyberpunk",
        "width": 1280,
        "height": 720
    })
```

---

## English

OpenFang Auto Clip includes a complete Agent Skills System compatible with OpenClaw framework for video automation tasks.

### Core Features

- **Skill Framework**: Extensible skill system with custom skill support
- **Workflows**: Combine multiple skills into complex workflows
- **Context Management**: Share variables and state across skills
- **Executor**: High-performance execution engine with parallel processing
- **Agent**: Intelligent agents encapsulating skills and workflows

### Available Skills

| Skill | Description | Parameters |
|-------|-------------|------------|
| `video_download` | Download video from URL | url, output_dir, quality |
| `video_transform` | Apply copyright transformation | input_path, preset, transform_level |
| `batch_process` | Process multiple videos in batch | urls, transform_level, parallel |
| `aigc_image` | Generate AI image | prompt, provider, style, variations |
| `aigc_video` | Generate AI video | prompt, provider, duration |
| `transcript_generate` | Generate video transcript | video_path, model, output_format |
| `clip_extract` | Extract clips from video | input_path, segments, output_dir |

### Quick Start

#### Python API

**Basic Skill Execution**

```python
from src.agent_skills import SkillExecutor

executor = SkillExecutor()

result = executor.execute(
    skill_name="video_download",
    params={
        "url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "output_dir": "./downloads"
    }
)

if result.success:
    print(f"Video downloaded: {result.data['video_path']}")
```

**Using Agent**

```python
from src.agent_skills import Agent, create_video_processing_workflow

agent = Agent(
    name="video_agent",
    description="Specialized video processing agent"
)

agent.add_skill("video_download")
agent.add_skill("video_transform")
agent.add_workflow(create_video_processing_workflow())

result = agent.execute(
    task="video_processing",
    params={
        "video_url": "https://www.youtube.com/watch?v=VIDEO_ID",
        "clip_segments": [(0, 30), (60, 90), (120, 150)]
    }
)
```

**Create Custom Skill**

```python
from src.agent_skills import Skill, SkillContext, SkillResult, SkillStatus, register_skill

@register_skill
class MyCustomSkill(Skill):
    """Custom skill example"""

    name = "my_custom_skill"
    description = "This is a custom skill"
    version = "1.0.0"
    author = "Your Name"

    parameters = {
        "input": {
            "type": str,
            "description": "Input parameter",
            "required": True
        }
    }

    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        input_value = kwargs.get("input")

        try:
            # Your processing logic
            result = f"Processed: {input_value}"

            return SkillResult(
                success=True,
                status=SkillStatus.COMPLETED,
                data={"result": result}
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.FAILED,
                error=str(e)
            )
```

### Preset Workflows

#### video_processing

Standard video processing: download → transform → extract clips

#### aigc_content

AI content generation: generate images → generate videos

#### full_pipeline

Complete pipeline: download → transform → transcript → clips

### Best Practices

1. **Modular Design**: Break complex tasks into small skills
2. **Reusable Workflows**: Create reusable workflow templates
3. **Error Handling**: Use stop_on_error=False for batch processing
4. **Variable References**: Use $variable_name to pass data between skills
5. **Conditional Execution**: Use condition parameter to control step execution
