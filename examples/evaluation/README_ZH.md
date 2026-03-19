# 评估路径索引

如果你想快速判断 `openfang-auto-clip` 现在值不值得继续看，这一页是最好的入口。

## 推荐顺序

1. 先跑一条命令的本地评估链路：

   ```bash
   python3 scripts/run_local_evaluation.py
   ```

2. 再看 synthetic benchmark 的说明：

   - [../benchmark/README_ZH.md](../benchmark/README_ZH.md)

3. 直接在 GitHub 查看已提交的 Level 2 样例产物：

   - [../demo/level2_samples/README_ZH.md](../demo/level2_samples/README_ZH.md)

4. 如果想看最新生成结果，再本地运行双语 Level 2 suite：

   ```bash
   python3 scripts/run_level2_demo_suite.py
   ```

5. 如果要看单个命令和操作路径，再看 demo 说明：

   - [../demo/README_ZH.md](../demo/README_ZH.md)

## 怎么选

- 最快证明仓库真实可跑：benchmark + benchmark summary
- 最安全的第一次本地试用：`run_local_evaluation.py`
- 最适合直接在 GitHub 浏览的 Level 2 证据：已提交的 `level2_samples/`
- 最适合看最新 Level 2 结果：`run_level2_demo_suite.py`

## 说明

- 这些评估路径默认都不需要下载真实源视频
- 只有当本地评估链路表现正常后，再去测试真实 URL
