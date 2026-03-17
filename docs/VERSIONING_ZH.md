# 版本管理说明

OpenFang Auto Clip 采用语义化版本管理。

## 标签格式

使用下面的 tag 形式：

```text
vMAJOR.MINOR.PATCH
```

例如：

- `v0.3.0`
- `v0.3.1`
- `v1.0.0`

## 含义

- `MAJOR`：CLI 或核心工作流有破坏性变更
- `MINOR`：新增向后兼容能力
- `PATCH`：修复、文档更新、稳定性增强、小行为修正

## 发布流程

1. 将已验证的变更合入 `main`
2. 运行 `python3 scripts/release_prep.py vX.Y.Z --report tmp/demo-benchmark-vXYZ/benchmark_report.json`
3. 如有需要，补充 changelog
4. 创建并推送 tag

```bash
git tag v0.3.0
git push origin main
git push origin v0.3.0
```

`release_prep.py` 现在会把下面这些东西一起打包：

- `release_notes.md`
- benchmark report 副本
- preview 和 storyboard 图片（如果存在）
- `launch_post.md`
- 中英文 social preview SVG

当 tag 推到 GitHub 后，`.github/workflows/release.yml` 会自动：

- 安装依赖
- 运行测试
- 生成 release notes
- 创建 GitHub Release

## 实践建议

- 还在快速变化阶段时继续使用 `0.x`
- 只有在 Level 1、Web 管理器、文档和发布链路都稳定后，再考虑 `1.0.0`
- 小步快跑比积压大版本更适合当前项目
