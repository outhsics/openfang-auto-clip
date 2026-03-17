# Showcase：本地 Web Manager Console

## 目标

把仓库展示成一个本地 operator console，而不只是命令行工具。

## 命令

```bash
./start_web_manager.sh
```

打开 `http://localhost:5000`。

## 重点展示什么

- 在浏览器里启动任务
- 处理前先校验 URL
- 本地任务历史
- 不依赖托管后端就能查看输出目录

## 为什么重要

- 对不熟悉终端的人更容易演示
- 给创作者和 operator 一个可视化入口
- 强化 local-first 叙事，同时不假装自己是 SaaS

## 适合使用的场景

- 录屏讲解
- 团队内部演示
- 和云端剪辑工具做对比
