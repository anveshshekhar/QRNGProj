import math
import sys
from collections import Counter
from scipy.stats import chisquare
from scipy.special import erfc

INPUT_FILE = "rng_data.txt"  
IGNORE_ZERO = True  
class Col:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Col.BOLD}{Col.CYAN}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Col.ENDC}")
def print_header2(text):
    print(f"\n{Col.BOLD}{Col.RED}{'='*60}")
    print(f" {text}")
    print(f"{'='*60}{Col.ENDC}")

def print_result(name, value, verdict, threshold_msg=""):
    if verdict == "PASS": color = Col.GREEN
    elif verdict == "WEAK": color = Col.YELLOW
    else: color = Col.RED
    
    print(f"{Col.BOLD}{name:<25}{Col.ENDC} : {value}")
    if threshold_msg:
        print(f"{' ':<25}   {Col.BLUE}({threshold_msg}){Col.ENDC}")
    print(f"{' ':<25} -> {color}[ {verdict} ]{Col.ENDC}")

def load_data(filename):
    data = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                clean = line.strip()
                if clean.isdigit():
                    val = int(clean)
                    if 0 <= val <= 255:
                        if IGNORE_ZERO and val == 0: continue
                        data.append(val)
    except FileNotFoundError:
        print(f"{Col.RED}Error: {filename} not found.{Col.ENDC}")
        sys.exit()
    return data
def test_mean(data):
    avg = sum(data) / len(data)
    expected = 128.0 if IGNORE_ZERO else 127.5
    diff = abs(avg - expected)
    
    status = "PASS"
    if diff > 2.0: status = "FAIL"
    elif diff > 1.0: status = "WEAK"
    
    return status, f"{avg:.4f}", f"Ideal: {expected}"
\
def test_monte_carlo_pi(data):
    hits = 0
    total_pairs = len(data) // 2
    
    for i in range(total_pairs):
        x = data[2*i] / 255.0
        y = data[2*i+1] / 255.0
        if (x*x + y*y) <= 1.0:
            hits += 1
            
    if total_pairs == 0: return "FAIL", "0.0000", "Insufficient Data"
    
    pi_est = 4.0 * (hits / total_pairs)
    error = abs(pi_est - math.pi) / math.pi * 100
    
    status = "PASS"
    if error > 5.0: status = "FAIL" 
    elif error > 2.5: status = "WEAK"
        
    return status, f"{pi_est:.5f}", f"Error: {error:.2f}%"

def test_entropy(data):
    counts = Counter(data)
    total = len(data)
    ent = 0
    for c in counts.values():
        p = c / total
        ent += -p * math.log2(p)
        
    max_ent = math.log2(255) if IGNORE_ZERO else 8.0
    status = "PASS" if ent > (max_ent - 0.05) else "FAIL"
    
    return status, f"{ent:.5f} bits", f"Max: {max_ent:.5f}"

def test_chi_square(data):
    counts = Counter(data)
    start = 1 if IGNORE_ZERO else 0
    obs = [counts[i] for i in range(start, 256)]
    stat, p = chisquare(obs)
    
    status = "PASS"
    if p < 0.001: status = "FAIL"
    elif p < 0.05: status = "WEAK"
    
    return status, f"P-Val: {p:.5f}", f"Stat: {stat:.2f}"

def test_autocorrelation(data):
    n = len(data)
    mean = sum(data)/n
    num = 0; den = 0
    for i in range(n-1):
        num += (data[i]-mean)*(data[i+1]-mean)
        den += (data[i]-mean)**2
    if den == 0: return "FAIL", "0.00", "DivByZero"
    
    corr = num / den
    status = "PASS" if abs(corr) < 0.05 else "FAIL"
    
    return status, f"Coeff: {corr:.5f}", "Threshold: +/- 0.05"

def test_nist_monobit(bit_string):
    n = len(bit_string)
    sn = bit_string.count('1') - bit_string.count('0')
    obs = abs(sn) / math.sqrt(n)
    p = erfc(obs / math.sqrt(2))
    
    status = "PASS" if p > 0.01 else "FAIL"
    return status, f"P-Val: {p:.5f}", f"Balance: {sn:+d}"

def test_nist_runs(bit_string):
    n = len(bit_string)
    pi = bit_string.count('1') / n
    if abs(pi - 0.5) >= (2 / math.sqrt(n)): return "FAIL", "0.0000", "Freq Fail"
    
    vn = 1 + sum(1 for i in range(n-1) if bit_string[i] != bit_string[i+1])
    num = abs(vn - 2*n*pi*(1-pi))
    den = 2 * math.sqrt(2*n) * pi * (1-pi)
    p = erfc(num/den)
    
    status = "PASS" if p > 0.01 else "FAIL"
    return status, f"P-Val: {p:.5f}", "Oscillation Check"

def main():
    print(f"\n{Col.BOLD}🔌 LOADING DATA...{Col.ENDC}")
    data = load_data(INPUT_FILE)
    bit_string = "".join([format(b, '08b') for b in data])
    
    print(f"   Loaded {len(data):,} bytes")
    print(f"   Analyzed {len(bit_string):,} bits")

    results = []
    print_header2("UNPROCESSED RAW RNG DATA")
    # 1. Simple Arithmetic
    print_header("1. BASIC STATISTICAL CHECKS")
    results.append(("Arithmetic Mean", *test_mean(data)))
    print_result(*results[-1])
    
    results.append(("Monte Carlo Pi", *test_monte_carlo_pi(data)))
    print_result(*results[-1])

    # 2. Information Theory
    print_header("2. INFORMATION & UNIFORMITY")
    results.append(("Shannon Entropy", *test_entropy(data)))
    print_result(*results[-1])
    
    results.append(("Chi-Square Test", *test_chi_square(data)))
    print_result(*results[-1])

    # 3. Hardware Checks
    print_header("3. HARDWARE & PATTERN CHECKS")
    results.append(("Autocorrelation", *test_autocorrelation(data)))
    print_result(*results[-1])

    results.append(("NIST Monobit", *test_nist_monobit(bit_string)))
    print_result(*results[-1])
    
    results.append(("NIST Runs", *test_nist_runs(bit_string)))
    print_result(*results[-1])

    # 4. FINAL REPORT
    print_header("🏁 FINAL REPORT CARD")
    failures = [name for name, status, _, _ in results if status == "FAIL"]
    
    if not failures:
        print(f"{Col.GREEN}{Col.BOLD}🏆 EXCELLENT! ALL TESTS PASSED.{Col.ENDC}")
        print("System is producing high-quality non-deterministic entropy.")
    else:
        print(f"{Col.RED}{Col.BOLD}⚠️  SYSTEM FAILED {len(failures)} TEST(S):{Col.ENDC}")
        for f in failures:
            print(f"   ❌ {f}")
        print(f"\n{Col.YELLOW}Note: Failures in Chi-Square or Runs are common for raw\nhardware sources without post-processing (SHA-256).{Col.ENDC}")

if __name__ == "__main__":
    main()