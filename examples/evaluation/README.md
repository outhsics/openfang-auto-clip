# Evaluation Paths

This page is the fastest way to understand how to evaluate `openfang-auto-clip` today.

## Recommended Order

1. Run the one-command local evaluation path:

   ```bash
   python3 scripts/run_local_evaluation.py
   ```

2. Inspect the synthetic benchmark walkthrough:

   - [../benchmark/README.md](../benchmark/README.md)

3. Inspect the committed Level 2 sample artifacts directly on GitHub:

   - [../demo/level2_samples/README.md](../demo/level2_samples/README.md)
   - [sample_local_evaluation_report.md](sample_local_evaluation_report.md)

4. Run the live bilingual Level 2 suite locally if you want fresh outputs:

   ```bash
   python3 scripts/run_level2_demo_suite.py
   ```

5. Use the operator-facing demo guide for individual commands:

   - [../demo/README.md](../demo/README.md)

6. Refresh the committed repo assets when you want GitHub-visible proof to stay current:

   ```bash
   python3 scripts/refresh_demo_assets.py
   ```

## Which Path To Use

- quickest repo proof: benchmark + benchmark summary
- safest first local trial: `run_local_evaluation.py`
- best GitHub-inspectable Level 2 proof: committed `level2_samples/`
- best fresh Level 2 validation: `run_level2_demo_suite.py`
- best GitHub-inspectable full evaluation snapshot: `sample_local_evaluation_report.md`

## Notes

- all of these paths avoid downloading real source media by default
- use real URLs only after the local evaluation path looks healthy
