# Social Preview 使用说明

仓库现在可以直接基于 benchmark report 生成一张可复用的社交预览图，用来增强 GitHub 仓库展示和对外传播效果。

## 为什么值得做

GitHub 仓库页本身就是增长入口。一个更强的 social preview 图可以提升：

- 仓库分享卡片点击率
- GitHub Release 展示质量
- X / LinkedIn / 微信等发布素材一致性
- README 文案和视觉证明之间的匹配度

## 生成命令

```bash
python3 scripts/generate_social_preview.py --report examples/benchmark/sample_benchmark_report.json
python3 scripts/generate_social_preview.py --report examples/benchmark/sample_benchmark_report.json --lang zh
```

输出目录：

```text
dist/social-preview/
├── github_social_preview.svg
└── github_social_preview_zh.svg
```

## 推荐流程

1. 先运行 benchmark
2. 再生成 social preview 图
3. 把英文版上传到 GitHub 仓库设置里的 social preview
4. 中文版用于中文发布帖、docs-site 截图或 release 素材

## 图片内容

- 项目定位
- 当前可验证信号
- benchmark 指标
- 仓库路径

## 对外表述建议

图片中的信息要和项目现状保持一致：

- 重点宣传 `CLI`、`Level 1`、`benchmark`、`storyboard`、`release flow`
- 不要把 `Level 2`、`Level 3` 包装成已经成熟交付的商业能力

## 相关文件

- `scripts/generate_social_preview.py`
- `examples/benchmark/sample_benchmark_report.json`
- `scripts/generate_launch_kit.py`
