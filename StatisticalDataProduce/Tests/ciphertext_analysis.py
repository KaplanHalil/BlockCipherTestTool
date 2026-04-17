"""
Ciphertext Statistical Analysis Tool
Reads the generated ciphertext file and performs comprehensive statistical tests
"""

import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from statistical_tests import run_all_tests, run_all_tests_parallel, print_test_results

def save_results_to_text_table(results, output_file="statistical_analysis_results.txt"):
    """Save statistical test results to a formatted text table"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("CIPHERTEXT STATISTICAL ANALYSIS RESULTS\n")
        f.write("="*80 + "\n\n")
        
        # Basic information
        f.write("DATA INFORMATION\n")
        f.write("-" * 20 + "\n")
        f.write(f"Data Length: {results['data_length']:,} bytes\n\n")
        
        # Entropy Analysis
        f.write("ENTROPY ANALYSIS\n")
        f.write("-" * 20 + "\n")
        f.write(f"{'Metric':<25} {'Value':<15} {'Ideal':<15} {'Status':<10}\n")
        f.write("-" * 65 + "\n")
        
        byte_entropy = results['entropy_byte']
        bit_entropy = results['entropy_bit']
        
        byte_status = "✓" if 7.9 <= byte_entropy <= 8.0 else "✗"
        bit_status = "✓" if 0.99 <= bit_entropy <= 1.0 else "✗"
        
        f.write(f"{'Byte Entropy':<25} {byte_entropy:<15.4f} {'8.0000':<15} {byte_status:<10}\n")
        f.write(f"{'Bit Entropy':<25} {bit_entropy:<15.4f} {'1.0000':<15} {bit_status:<10}\n\n")
        f.write("Remarks: High byte entropy and bit entropy indicate that the ciphertext is highly unpredictable at both byte and bit levels.\n\n")
        
        # Chi-Square Test
        f.write("CHI-SQUARE TEST\n")
        f.write("-" * 20 + "\n")
        chi_square = results['chi_square']
        chi_status = "✓" if 200 <= chi_square <= 300 else "✗"
        f.write(f"{'Chi-Square Value':<25} {chi_square:<15.2f} {'200-300':<15} {chi_status:<10}\n\n")
        f.write("Remarks: The chi-square result measures how close byte frequencies are to a uniform distribution. A value inside the expected range means the ciphertext has no obvious byte bias.\n\n")
        
        # Byte Frequency Analysis
        f.write("BYTE FREQUENCY ANALYSIS\n")
        f.write("-" * 25 + "\n")
        bf = results['byte_frequency']
        f.write(f"{'Metric':<25} {'Value':<15} {'Ideal':<15}\n")
        f.write("-" * 55 + "\n")
        f.write(f"{'Average Frequency':<25} {bf['avg_frequency']:<15.6f} {'0.003906':<15}\n")
        f.write(f"{'Standard Deviation':<25} {bf['std_dev']:<15.6f} {'~0.0000':<15}\n")
        f.write(f"{'Min Frequency':<25} {bf['min_freq']:<15.6f} {'~0.0039':<15}\n")
        f.write(f"{'Max Frequency':<25} {bf['max_freq']:<15.6f} {'~0.0039':<15}\n\n")
        f.write("Remarks: Small standard deviation and min/max values close to 1/256 show the byte distribution is close to uniform.\n\n")
        
        # Bit Frequency Analysis
        f.write("BIT FREQUENCY ANALYSIS\n")
        f.write("-" * 25 + "\n")
        bitf = results['bit_frequency']
        f.write(f"{'Metric':<25} {'Value':<15} {'Ideal':<15} {'Status':<10}\n")
        f.write("-" * 65 + "\n")
        
        ones_status = "✓" if 0.49 <= bitf['ones_ratio'] <= 0.51 else "✗"
        zeros_status = "✓" if 0.49 <= bitf['zeros_ratio'] <= 0.51 else "✗"
        bias_status = "✓" if bitf['bias'] <= 0.01 else "✗"
        
        f.write(f"{'Ones Ratio':<25} {bitf['ones_ratio']:<15.4f} {'0.5000':<15} {ones_status:<10}\n")
        f.write(f"{'Zeros Ratio':<25} {bitf['zeros_ratio']:<15.4f} {'0.5000':<15} {zeros_status:<10}\n")
        f.write(f"{'Bit Bias':<25} {bitf['bias']:<15.4f} {'0.0000':<15} {bias_status:<10}\n\n")
        f.write("Remarks: Balanced ones and zeros ratios tell us there is no strong bit bias in the ciphertext.\n\n")
        
        # Autocorrelation Analysis
        f.write("AUTOCORRELATION ANALYSIS\n")
        f.write("-" * 25 + "\n")
        ac = results['autocorrelation']
        f.write(f"{'Metric':<25} {'Value':<15} {'Ideal':<15} {'Status':<10}\n")
        f.write("-" * 65 + "\n")
        
        avg_corr_status = "✓" if abs(ac['avg_correlation']) <= 0.01 else "✗"
        max_corr_status = "✓" if abs(ac['max_correlation']) <= 0.01 else "✗"
        
        f.write(f"{'Average Correlation':<25} {ac['avg_correlation']:<15.6f} {'~0.0000':<15} {avg_corr_status:<10}\n")
        f.write(f"{'Max Correlation':<25} {ac['max_correlation']:<15.6f} {'~0.0000':<15} {max_corr_status:<10}\n")
        f.write(f"{'Number of Lags':<25} {len(ac['lags']):<15} {'100':<15}\n\n")
        f.write("Remarks: Low autocorrelation values indicate ciphertext bits are effectively decorrelated across lags.\n\n")
        
        # Summary
        f.write("SUMMARY\n")
        f.write("-" * 10 + "\n")
        all_good = all([
            7.9 <= byte_entropy <= 8.0,
            0.99 <= bit_entropy <= 1.0,
            200 <= chi_square <= 300,
            0.49 <= bitf['ones_ratio'] <= 0.51,
            0.49 <= bitf['zeros_ratio'] <= 0.51,
            bitf['bias'] <= 0.01,
            abs(ac['avg_correlation']) <= 0.01,
            abs(ac['max_correlation']) <= 0.01
        ])
        
        if all_good:
            f.write("✓ All statistical tests PASSED \n")
        else:
            f.write("✗ Some statistical tests FAILED \n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("Analysis completed on: " + os.popen('date').read().strip() + "\n")
    
    print(f"Results saved to {output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Ciphertext Statistical Analysis Tool')
    parser.add_argument('--parallel', action='store_true', help='Run tests in parallel for better performance')
    parser.add_argument('--workers', type=int, default=None, help='Number of worker processes for parallel execution')
    
    args = parser.parse_args()
    
    ciphertext_file = "Results/ciphertext.hex"
    
    if not os.path.exists(ciphertext_file):
        print(f"Error: {ciphertext_file} not found!")
        print("Please run ctr_write_to_folder.py first to generate ciphertext.")
        return
    
    print("="*60)
    print("CIPHERTEXT STATISTICAL ANALYSIS")
    print("="*60)
    
    # Read the ciphertext
    print(f"\nReading ciphertext from {ciphertext_file}...")
    with open(ciphertext_file, "rb") as f:
        ciphertext_data = f.read()
    
    print(f"Ciphertext size: {len(ciphertext_data)} bytes")
    
    # Run all statistical tests
    if args.parallel:
        print(f"\nRunning statistical tests in parallel (workers: {args.workers or 'auto'})...")
        results = run_all_tests_parallel(ciphertext_data, max_workers=args.workers)
    else:
        print("\nRunning statistical tests sequentially...")
        results = run_all_tests(ciphertext_data)
    
    # Print results
    print_test_results(results)
    
    # Save results to text table
    save_results_to_text_table(results)

if __name__ == "__main__":
    main()
