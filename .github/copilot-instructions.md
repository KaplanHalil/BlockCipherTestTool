---
name: BlockCipherTestTool Workspace Instructions
description: "Project-level guidance for using and extending BlockCipherTestTool."
---

# Workspace bootstrap instructions

## Purpose
This workspace is a block cipher testing tool built around Python scripts, shell orchestration, and SageMath for S-box analysis. The bootstrap file helps AI agents understand project structure, test commands, and the main conventions used here.

## Key commands
- Run the main workflow from the repository root:
  - `bash run_tests.sh`
- The script currently uses `python3` and requires `sage` for S-box testing.
- `run_tests.sh` generates `Algorithm/Alg.py` at runtime based on the selected cipher name.

## Important directories
- `Algorithm/` — cipher implementations and helper modules.
- `AvalCorrTests/` — avalanche and correlation test scripts.
- `StatisticalDataProduce/` — ciphertext generation and statistical analysis scripts.
- `SboxTest/` — S-box analysis using SageMath.
- `Results/` — output files created by test scripts.

## Conventions and caveats
- `run_tests.sh` is the main entrypoint; many test commands are currently commented out.
- Do not edit generated `Algorithm/Alg.py` directly; the workflow rewrites it from the selected algorithm name.
- Statistical test scripts write results into `Results/` and may also move generated files such as `ciphertext.hex`, `statistical_analysis_results.txt`, `BCT.png`, and `DDT.png`.
- S-box tests are invoked through Sage and may require `sage` available on the PATH.

## Agent guidance
- When asked to extend or debug tests, prefer changes in `Run_tests.sh`, `AvalCorrTests/`, and `StatisticalDataProduce/`.
- When adding a new cipher, create a new module under `Algorithm/` and update the selected algorithm name in `run_tests.sh`.
- When improving S-box analysis, inspect `SboxTest/README.md` and the Sage files.

## Example prompts
- "Update `run_tests.sh` so avalanche and correlation tests can be enabled via flags."
- "Add a new cipher module to `Algorithm/` and wire it into the existing test workflow."
- "Document how the statistical tests generate ciphertext and output results into `Results/`."
