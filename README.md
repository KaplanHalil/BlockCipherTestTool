# BlockCipherTestTool

## Analysis Program

This repository is designed to generate randomness and cryptanalysis tests for block ciphers.

The main workflow is executed through `run_tests.sh`. This script performs the following steps:

- Loads the selected algorithm in `Algorithm/Alg.py`.
- Generates ciphertext for testing with `StatisticalDataProduce/DataGeneration/ctr_write_to_folder.py`.
- Runs interpolation resistance analysis with `InterpolationTests/interpolation_attack_test.py`.
- Creates a statistical analysis report with `StatisticalDataProduce/Tests/ciphertext_analysis.py`.

### Directory structure

- `StatisticalDataProduce/DataGeneration/`: ciphertext generation and data preparation scripts.
- `StatisticalDataProduce/Tests/`: statistical test scripts such as entropy, chi-square, frequency, and autocorrelation.
- `InterpolationTests/`: specialized interpolation analysis scripts.

The interpolation analysis evaluates whether ciphertext bits can be described by low-degree Boolean polynomials of selected plaintext byte positions.
It builds a truth table over a plaintext subspace, derives Algebraic Normal Form (ANF) for each output bit, and reports degree and coefficient sparsity.
Low-degree or sparse ANF results may indicate stronger susceptibility to interpolation-style algebraic analysis.

### Usage

Run from the project root:

```bash
sh run_tests.sh
```

This executes the data generation and the interpolation + statistical analysis steps in sequence.

### Results

Generated reports are saved to the `Results/` folder. The interpolation analysis output is specifically saved in `Results/interpolation_attack_test.txt`.

---

Planned enhancements:

- Add SAC to the S-box test
- Review S-box component functions
- Convert acall-corr plotting from 1D array to 2D drawing
- Add cube attack
- Add square attack
- Add interpolation testing
- Add d-monom test
- Add slender test
- Add integral analysis test
- Add test vector validation

