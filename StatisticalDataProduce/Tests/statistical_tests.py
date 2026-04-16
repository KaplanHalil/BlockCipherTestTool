"""
Statistical tests for ciphertext analysis
Includes: entropy, chi-square, frequency analysis, autocorrelation
"""

import math
import os
from collections import Counter
import concurrent.futures
import multiprocessing

# Global wrapper functions for ProcessPoolExecutor (must be at module level to be picklable)
def _entropy_byte_test(data):
    return calculate_entropy(data)

def _entropy_bit_test(data):
    return calculate_bit_entropy(data)

def _chi_square_test_wrapper(data):
    return chi_square_test(data)

def _byte_freq_test(data):
    return byte_frequency_analysis(data)

def _bit_freq_test(data):
    return bit_frequency_analysis(data)

def _autocorr_test(data):
    return autocorrelation_analysis(data)

def calculate_entropy(data):
    """
    Calculate Shannon entropy of the data.
    Entropy measures randomness. For perfectly random data:
    - Byte entropy should be close to 8 bits
    - Bit entropy should be close to 1 bit
    """
    if isinstance(data, list):
        data = bytes(data)
    
    byte_counts = Counter(data)
    entropy = 0
    data_len = len(data)
    
    for count in byte_counts.values():
        probability = count / data_len
        entropy -= probability * math.log2(probability)
    
    return entropy

def calculate_bit_entropy(data):
    """Calculate entropy at bit level"""
    if isinstance(data, list):
        data = bytes(data)
    
    bit_string = ''.join(format(byte, '08b') for byte in data)
    bit_counts = Counter(bit_string)
    bit_entropy = 0
    bit_len = len(bit_string)
    
    for count in bit_counts.values():
        probability = count / bit_len
        bit_entropy -= probability * math.log2(probability)
    
    return bit_entropy

def chi_square_test(data):
    """
    Perform chi-square test on ciphertext.
    Returns chi-square value and p-value interpretation.
    For random data, chi-square should be close to 256 (number of possible byte values).
    """
    if isinstance(data, list):
        data = bytes(data)
    
    byte_counts = Counter(data)
    expected_frequency = len(data) / 256
    chi_square = 0
    
    for i in range(256):
        observed = byte_counts.get(i, 0)
        chi_square += ((observed - expected_frequency) ** 2) / expected_frequency
    
    return chi_square

def byte_frequency_analysis(data):
    """
    Analyze byte frequency distribution.
    Returns distribution statistics.
    """
    if isinstance(data, list):
        data = bytes(data)
    
    byte_counts = Counter(data)
    total_bytes = len(data)
    
    frequencies = [byte_counts.get(i, 0) / total_bytes for i in range(256)]
    
    # Calculate statistics
    avg_freq = 1.0 / 256
    variance = sum((f - avg_freq) ** 2 for f in frequencies) / 256
    std_dev = math.sqrt(variance)
    
    return {
        'avg_frequency': avg_freq,
        'std_dev': std_dev,
        'min_freq': min(frequencies),
        'max_freq': max(frequencies),
        'variance': variance
    }

def bit_frequency_analysis(data):
    """
    Analyze bit frequency distribution.
    For good ciphers, bit frequency should be close to 0.5 for both 0 and 1.
    """
    if isinstance(data, list):
        data = bytes(data)
    
    bit_string = ''.join(format(byte, '08b') for byte in data)
    ones = bit_string.count('1')
    zeros = bit_string.count('0')
    total_bits = len(bit_string)
    
    ones_ratio = ones / total_bits
    zeros_ratio = zeros / total_bits
    
    return {
        'ones_ratio': ones_ratio,
        'zeros_ratio': zeros_ratio,
        'bias': abs(ones_ratio - 0.5),
        'total_bits': total_bits
    }

def autocorrelation_analysis(data, max_lag=100):
    """
    Analyze autocorrelation at different lags.
    Good ciphers should have low autocorrelation.
    """
    if isinstance(data, list):
        data = bytes(data)
    
    correlations = []
    data_len = len(data)
    
    # Use bit representation for autocorrelation
    bit_array = [int(bit) for byte_val in data for bit in format(byte_val, '08b')]
    
    mean = sum(bit_array) / len(bit_array)
    
    for lag in range(1, min(max_lag + 1, len(bit_array) // 2)):
        covariance = 0
        for i in range(len(bit_array) - lag):
            covariance += (bit_array[i] - mean) * (bit_array[i + lag] - mean)
        
        variance = sum((bit - mean) ** 2 for bit in bit_array)
        correlation = covariance / variance if variance != 0 else 0
        correlations.append(correlation)
    
    return {
        'lags': list(range(1, len(correlations) + 1)),
        'correlations': correlations,
        'avg_correlation': sum(correlations) / len(correlations) if correlations else 0,
        'max_correlation': max(correlations) if correlations else 0
    }

def run_all_tests(data):
    """
    Run all statistical tests on the ciphertext.
    Returns a dictionary with all test results.
    """
    if isinstance(data, list):
        data = bytes(data)
    
    results = {
        'data_length': len(data),
        'entropy_byte': calculate_entropy(data),
        'entropy_bit': calculate_bit_entropy(data),
        'chi_square': chi_square_test(data),
        'byte_frequency': byte_frequency_analysis(data),
        'bit_frequency': bit_frequency_analysis(data),
        'autocorrelation': autocorrelation_analysis(data)
    }
    
    return results

def run_all_tests_parallel(data, max_workers=None):
    """
    Run all statistical tests in parallel for better performance.
    Uses ThreadPoolExecutor for I/O bound tasks and lighter CPU tasks.
    For heavy CPU-bound tasks, consider using ProcessPoolExecutor.
    Returns a dictionary with all test results.
    """
    if isinstance(data, list):
        data = bytes(data)
    
    if max_workers is None:
        max_workers = min(multiprocessing.cpu_count(), 6)  # Use up to 6 workers
    
    # Define test functions that can run in parallel
    test_functions = {
        'entropy_byte': lambda: calculate_entropy(data),
        'entropy_bit': lambda: calculate_bit_entropy(data),
        'chi_square': lambda: chi_square_test(data),
        'byte_frequency': lambda: byte_frequency_analysis(data),
        'bit_frequency': lambda: bit_frequency_analysis(data),
        'autocorrelation': lambda: autocorrelation_analysis(data)
    }
    
    results = {'data_length': len(data)}
    
    # Use ThreadPoolExecutor for better compatibility and lower overhead
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_test = {executor.submit(func): test_name for test_name, func in test_functions.items()}
        
        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_test):
            test_name = future_to_test[future]
            try:
                results[test_name] = future.result()
            except Exception as exc:
                print(f'Test {test_name} generated an exception: {exc}')
                results[test_name] = None
    
    return results


def interpret_entropy(byte_entropy, bit_entropy):
    lines = []
    lines.append("Byte entropy measures how unpredictable the ciphertext bytes are.")
    lines.append("Values close to 8.0 indicate a near-uniform distribution of byte values.")
    if byte_entropy >= 7.9:
        lines.append("Result: Strong byte-level randomness.")
    else:
        lines.append("Result: Byte entropy is lower than ideal; this may indicate uneven byte distribution.")
    lines.append("")
    lines.append("Bit entropy measures randomness at the individual bit level.")
    lines.append("Values close to 1.0 mean the bits are well balanced between 0 and 1.")
    if bit_entropy >= 0.99:
        lines.append("Result: Strong bit-level randomness.")
    else:
        lines.append("Result: Bit entropy is lower than expected; there may be bit bias.")
    return lines


def interpret_chi_square(chi_square):
    lines = []
    lines.append("The chi-square statistic measures how close the byte frequency distribution is to uniform.")
    lines.append("For a well-randomized ciphertext, values around 200-300 are expected for large samples.")
    if 200 <= chi_square <= 300:
        lines.append("Result: Chi-square is within the normal random-data range.")
    elif chi_square < 200:
        lines.append("Result: Chi-square is unusually low; this can indicate too little variation.")
    else:
        lines.append("Result: Chi-square is unusually high; this can indicate byte frequency bias.")
    return lines


def interpret_byte_frequency(bf):
    lines = []
    lines.append("Byte frequency analysis checks how evenly the 256 possible byte values appear.")
    lines.append("Average frequency should be close to 1/256, and low standard deviation is desired.")
    lines.append(f"Observed average frequency: {bf['avg_frequency']:.8f}, ideal: {1/256:.8f}.")
    lines.append(f"Observed standard deviation: {bf['std_dev']:.8f}; lower values indicate more uniform byte distribution.")
    if bf['std_dev'] <= 0.00005:
        lines.append("Result: Byte frequencies are very uniform.")
    else:
        lines.append("Result: Byte frequency variation is larger than ideal; this may suggest minor bias.")
    return lines


def interpret_bit_frequency(bitf):
    lines = []
    lines.append("Bit frequency analysis checks whether the ciphertext bits are balanced.")
    lines.append("A good result has ones and zeros close to a 50/50 split.")
    lines.append(f"Ones ratio: {bitf['ones_ratio']:.6f}, zeros ratio: {bitf['zeros_ratio']:.6f}.")
    lines.append(f"Bit bias: {bitf['bias']:.6f}; values near 0.0 are best.")
    if bitf['bias'] <= 0.01:
        lines.append("Result: Bit distribution is well balanced.")
    else:
        lines.append("Result: Bit distribution shows noticeable bias.")
    return lines


def interpret_autocorrelation(ac):
    lines = []
    lines.append("Autocorrelation measures whether ciphertext bits repeat or correlate across offsets.")
    lines.append("Low autocorrelation values close to zero are expected for good ciphertext.")
    lines.append(f"Average correlation: {ac['avg_correlation']:.6f}, max correlation: {ac['max_correlation']:.6f}.")
    if abs(ac['max_correlation']) <= 0.01:
        lines.append("Result: No strong linear correlation detected across bit lags.")
    else:
        lines.append("Result: Some correlation is present; this may suggest weak diffusion.")
    return lines

RESULT_FILE = "Results/statistical_analysis_results.txt"


def format_all_results(results):
    """Build a single textual report for all statistical tests."""
    bf = results['byte_frequency']
    bitf = results['bit_frequency']
    ac = results['autocorrelation']

    entropy_explanation = interpret_entropy(results['entropy_byte'], results['entropy_bit'])
    chi_explanation = interpret_chi_square(results['chi_square'])
    byte_freq_explanation = interpret_byte_frequency(bf)
    bit_freq_explanation = interpret_bit_frequency(bitf)
    autocorr_explanation = interpret_autocorrelation(ac)

    output_lines = [
        "STATISTICAL ANALYSIS RESULTS",
        "========================================",
        f"Data Length: {results['data_length']} bytes",
        "",
        "--- ENTROPY ANALYSIS ---",
        f"Byte Entropy: {results['entropy_byte']:.6f} bits (max: 8.000000)",
        f"Bit Entropy: {results['entropy_bit']:.6f} bits (max: 1.000000)",
        "",
        "Entropy Interpretation:",
    ]
    output_lines += [f"- {line}" for line in entropy_explanation]
    output_lines += [
        "",
        "--- CHI-SQUARE TEST ---",
        f"Chi-Square Value: {results['chi_square']:.6f}",
        "Expected range for random data: ~200-300",
        "",
        "Chi-Square Interpretation:",
    ]
    output_lines += [f"- {line}" for line in chi_explanation]
    output_lines += [
        "",
        "--- BYTE FREQUENCY ANALYSIS ---",
        f"Average Frequency: {bf['avg_frequency']:.8f}",
        f"Standard Deviation: {bf['std_dev']:.8f}",
        f"Min Frequency: {bf['min_freq']:.8f}",
        f"Max Frequency: {bf['max_freq']:.8f}",
        "",
        "Byte Frequency Interpretation:",
    ]
    output_lines += [f"- {line}" for line in byte_freq_explanation]
    output_lines += [
        "",
        "--- BIT FREQUENCY ANALYSIS ---",
        f"Ones Ratio: {bitf['ones_ratio']:.6f} (ideal: 0.500000)",
        f"Zeros Ratio: {bitf['zeros_ratio']:.6f} (ideal: 0.500000)",
        f"Bit Bias: {bitf['bias']:.6f}",
        "",
        "Bit Frequency Interpretation:",
    ]
    output_lines += [f"- {line}" for line in bit_freq_explanation]
    output_lines += [
        "",
        "--- AUTOCORRELATION ANALYSIS ---",
        f"Average Correlation: {ac['avg_correlation']:.6f}",
        f"Max Correlation: {ac['max_correlation']:.6f}",
        f"Number of Lags: {len(ac['lags'])}",
        "",
        "Autocorrelation Interpretation:",
    ]
    output_lines += [f"- {line}" for line in autocorr_explanation]
    output_lines += [
        "",
        "Lag,Correlation",
    ]

    for lag, correlation in zip(ac['lags'], ac['correlations']):
        output_lines.append(f"{lag},{correlation:.8f}")

    return "\n".join(output_lines) + "\n"


def print_test_results(results):
    """Pretty print statistical test results."""
    print("\n" + "="*60)
    print("STATISTICAL ANALYSIS RESULTS")
    print("="*60)

    print(f"\nData Length: {results['data_length']} bytes")

    print("\n--- ENTROPY ANALYSIS ---")
    print(f"Byte Entropy: {results['entropy_byte']:.4f} bits (max: 8.0)")
    print(f"Bit Entropy: {results['entropy_bit']:.4f} bits (max: 1.0)")
    entropy_explanation = interpret_entropy(results['entropy_byte'], results['entropy_bit'])
    for line in entropy_explanation:
        print(f"  - {line}")

    print("\n--- CHI-SQUARE TEST ---")
    print(f"Chi-Square Value: {results['chi_square']:.2f}")
    print("Expected ~ 256 for random data")
    chi_explanation = interpret_chi_square(results['chi_square'])
    for line in chi_explanation:
        print(f"  - {line}")

    print("\n--- BYTE FREQUENCY ANALYSIS ---")
    bf = results['byte_frequency']
    print(f"Average Frequency: {bf['avg_frequency']:.6f}")
    print(f"Standard Deviation: {bf['std_dev']:.6f}")
    print(f"Min Frequency: {bf['min_freq']:.6f}")
    print(f"Max Frequency: {bf['max_freq']:.6f}")
    byte_freq_explanation = interpret_byte_frequency(bf)
    for line in byte_freq_explanation:
        print(f"  - {line}")

    print("\n--- BIT FREQUENCY ANALYSIS ---")
    bitf = results['bit_frequency']
    print(f"Ones Ratio: {bitf['ones_ratio']:.4f} (ideal: 0.5000)")
    print(f"Zeros Ratio: {bitf['zeros_ratio']:.4f} (ideal: 0.5000)")
    print(f"Bit Bias: {bitf['bias']:.4f} (ideal: 0.0000)")

    bit_explanation = interpret_bit_frequency(bitf)
    for line in bit_explanation:
        print(f"  - {line}")

    print("\n--- AUTOCORRELATION ANALYSIS ---")
    ac = results['autocorrelation']
    print(f"Average Correlation: {ac['avg_correlation']:.6f}")
    print(f"Max Correlation: {ac['max_correlation']:.6f}")

    autocorr_explanation = interpret_autocorrelation(ac)
    for line in autocorr_explanation:
        print(f"  - {line}")


def write_results_to_file(text, filepath=RESULT_FILE):
    """Write the combined report to the results file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as out:
        out.write(text)


def main():
    ciphertext_file = "ciphertext.hex"
    if not os.path.exists(ciphertext_file):
        print(f"Error: {ciphertext_file} not found. Generate ciphertext first.")
        return

    with open(ciphertext_file, "rb") as f:
        data = f.read()

    results = run_all_tests(data)
    output = format_all_results(results)
    write_results_to_file(output, RESULT_FILE)

    print(f"Combined statistical analysis saved to {RESULT_FILE}")


if __name__ == "__main__":
    main()
    
    print("\n" + "="*60)
