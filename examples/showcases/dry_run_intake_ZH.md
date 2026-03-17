# Showcase：Dry-Run Intake Flow

## 目标

展示在真正下载或转换素材前，最稳妥的评估路径是什么。

## 命令

```bash
./auto_clip.sh --doctor
./auto_clip.sh "https://www.youtube.com/watch?v=VIDEO_ID" --dry-run
```

## 这能证明什么

- 本地必需工具都已经在 PATH 上
- 输出目录能正确解析
- 在不消耗真实处理成本前，仓库就能生成执行计划

## 为什么重要

- 降低首次演示失败风险
- 给 operator 一个清晰的 preflight 步骤
- 比直接让用户下载真实视频更适合作为第一次体验

## 适合使用的场景

- 安装指南
- operator onboarding
- Discussions 里的支持回复
