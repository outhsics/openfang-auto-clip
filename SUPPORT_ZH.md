# 支持

## 去哪里提什么问题

- Bug：GitHub Issues
- 功能建议：GitHub Issues 或 Discussions
- 使用问题：GitHub Discussions
- 安全问题：按 [SECURITY.md](SECURITY.md) 里的方式处理

## 发帖前请尽量带上这些信息

- 你的操作系统和 Python 版本
- `./auto_clip.sh --doctor` 是否通过
- 你实际运行的命令
- 完整错误输出
- 你使用的是本地媒体、synthetic benchmark 媒体，还是远程 URL

## 最快评估路径

如果你是第一次接触这个项目，先不要直接调真实 URL，建议先这样走：

1. 运行 `./auto_clip.sh --doctor`
2. 运行 `python3 scripts/run_local_evaluation.py`
3. 查看生成的本地评估报告、benchmark 产物和 Level 2 suite 结果
4. 再开始测试真实 URL
