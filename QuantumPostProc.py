import math
import hashlib
import os
import sys
from collections import Counter
from scipy.stats import chisquare
from scipy.special import erfc

INPUT_FILE = "rng_data.txt"
OUTPUT_FILE = "processed_rng.txt"

def load_data(filename):
    print("Reading file...")
    data = []
    if not os.path.exists(filename):
        print(f"Error: File {filename} not found.")
        return []

    try:
        with open(filename, 'r', encoding='utf-8-sig') as f:
            for line in f:
                clean = line.strip()
                if clean.isdigit():
                    val = int(clean)
                    if 0 <= val <= 255:
                        data.append(val)
    except Exception as e:
        print(f"Error reading file: {e}")
        return []
        
    print(f"Successfully loaded {len(data)} integers.")
    return data

def save_data(filename, data):
    print(f"Saving processed data to {filename}...")
    try:
        with open(filename, 'w') as f:
            for val in data:
                f.write(f"{val}\n")
        print("Save successful.")
    except Exception as e:
        print(f"Error saving file: {e}")

def quantum_safe_processing(raw_data):
    print("Running SHAKE-256 Sponge construction...")
    raw_bytes = bytes(raw_data)
    sponge = hashlib.shake_256()
    sponge.update(raw_bytes)
    clean_bytes = sponge.digest(len(raw_data))
    return [b for b in clean_bytes]

def run_tests(name, data):
    count = len(data)
    if count == 0:
        return {}
    
    counts = Counter(data)
    entropy = 0
    for c in counts.values():
        p = c / count
        entropy += -p * math.log2(p)
        
    obs = [counts[i] for i in range(256)]
    chi_stat, chi_p = chisquare(obs)
    
    bit_string = "".join([format(b, '08b') for b in data])
    n_bits = len(bit_string)
    sn = bit_string.count('1') - bit_string.count('0')
    monobit_stat = abs(sn) / math.sqrt(n_bits)
    monobit_p = erfc(monobit_stat / math.sqrt(2))
    
    mean = sum(data) / count
    
    return {
        "name": name,
        "entropy": entropy,
        "chi_p": chi_p,
        "monobit_p": monobit_p,
        "mean": mean,
        "samples": count
    }

def print_report(res_raw, res_clean):
    print("\n" + "="*70)
    print(" COMPARATIVE ANALYSIS: RAW vs QUANTUM-SAFE PROCESSED")
    print("="*70)
    
    headers = ["METRIC", "RAW DATA", "PROCESSED", "STATUS"]
    print(f"{headers[0]:<20} | {headers[1]:<20} | {headers[2]:<20} | {headers[3]}")
    print("-" * 70)
    
    e1 = res_raw['entropy']
    e2 = res_clean['entropy']
    imp_ent = "IMPROVED" if e2 > e1 else "SAME"
    print(f"{'Shannon Entropy':<20} | {e1:.5f} bits         | {e2:.5f} bits         | {imp_ent}")

    m1 = res_raw['mean']
    m2 = res_clean['mean']
    dist1 = abs(m1 - 127.5)
    dist2 = abs(m2 - 127.5)
    imp_mean = "CENTERED" if dist2 < dist1 else "BIASED"
    print(f"{'Arithmetic Mean':<20} | {m1:.4f}             | {m2:.4f}             | {imp_mean}")

    cp1 = res_raw['chi_p']
    cp2 = res_clean['chi_p']
    stat_chi = "PASS" if cp2 > 0.05 else "FAIL"
    cp1_str = f"{cp1:.4f}" if cp1 > 0.0001 else f"{cp1:.2e}"
    cp2_str = f"{cp2:.4f}" if cp2 > 0.0001 else f"{cp2:.2e}"
    print(f"{'Chi-Square P-Val':<20} | {cp1_str:<20} | {cp2_str:<20} | {stat_chi}")

    np1 = res_raw['monobit_p']
    np2 = res_clean['monobit_p']
    stat_mono = "PASS" if np2 > 0.01 else "FAIL"
    np1_str = f"{np1:.4f}" if np1 > 0.0001 else f"{np1:.2e}"
    np2_str = f"{np2:.4f}" if np2 > 0.0001 else f"{np2:.2e}"
    print(f"{'NIST Monobit P':<20} | {np1_str:<20} | {np2_str:<20} | {stat_mono}")
    
    print("-" * 70)

def main():
    print("Starting Analysis...")
    raw_data = load_data(INPUT_FILE)
    if not raw_data:
        print("No valid data found in rng_data.txt")
        return

    results_raw = run_tests("Raw Hardware", raw_data)
    processed_data = quantum_safe_processing(raw_data)
    results_clean = run_tests("SHAKE-256", processed_data)
    
    print_report(results_raw, results_clean)
    
    save_data(OUTPUT_FILE, processed_data)
    print("Analysis Complete.")

if __name__ == "__main__":
    main()