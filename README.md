# Quantum-Safe TRNG (ESP32 + SHAKE-256)

**A True Random Number Generator (TRNG) utilizing quantum noise from ESP32 silicon, stabilized by Von Neumann whitening and post-processed using a Cryptographic Sponge construction.**

##  Project Overview
This project harvests true entropy from thermal/quantum noise inherent in the ESP32's ADC (Analog-to-Digital Converter). Unlike pseudo-random number generators (PRNGs) like `rand()`, which are deterministic, this system produces non-deterministic data based on physical phenomena.

To align with **NIST Post-Quantum Cryptography (PQC)** standards, the raw entropy is post-processed using a **SHAKE-256 Sponge Construction**. This removes hardware bias and ensures the output is cryptographically uniform and unpredictable.

##  Key Features
* **Entropy Source:** Floating GPIO pin on ESP32 measuring avalanche noise and thermal fluctuations.
* **Hardware Whitening:** Real-time Von Neumann debiasing implemented in firmware (0/1 pair logic).
* **Visualization:** Real-time graphing of entropy on an **ILI9225 TFT Display**.
* **Quantum-Safe Processing:** Python-based implementation of the **SHAKE-256** (Keccak) sponge function to extract perfect randomness from biased physical sources.
* **Statistical Validation:** Automated test suite verifying Shannon Entropy, Chi-Square Uniformity, and NIST Monobit tests.

## 🛠️ Hardware Setup
* **Microcontroller:** ESP32 Dev Module
* **Display:** 2.2" TFT ILI9225
* **Input:** Floating Wire (Antenna) on `GPIO 34` (Analog Input)
* **Control:** Push Button on `GPIO 0` (Pause/Resume)

### Wiring Diagram
| Component Pin | ESP32 Pin | Function |
| :--- | :--- | :--- |
| **TFT CLK** | GPIO 18 | SPI Clock |
| **TFT SDI** | GPIO 23 | SPI MOSI |
| **TFT CS** | GPIO 5 | Chip Select |
| **TFT RST** | GPIO 4 | Reset |
| **TFT RS** | GPIO 2 | Register Select |
| **ENTROPY** | GPIO 34 | **Floating Input (Source)** |
| **BUTTON** | GPIO 0 | Pause Control |

##  Theory of Operation
The randomness pipeline consists of three stages:

1.  **Raw Extraction:** The ADC samples the floating voltage on GPIO 34. This signal is dominated by thermal noise and electromagnetic interference.
2.  **Debiasing (Firmware):** The ESP32 applies **Von Neumann Whitening**:
    * Read two bits: `b1`, `b2`.
    * If `01` → Output `0`.
    * If `10` → Output `1`.
    * If `00` or `11` → Discard.
3.  **Privacy Amplification (Software):** The raw bytes are fed into a **SHAKE-256 Sponge**. This absorbs the bitstream into a massive internal state and "squeezes" out a chemically pure random stream, removing any residual sensor bias (e.g., temperature drift).



##  Software & Usage

### 1. Firmware (ESP32)
Flash the standard `.ino` file to the ESP32.
* **Display:** Shows the current 8-bit integer, a running graph, and real-time Mean/Variance stats.
* **Serial Output:** Streams raw integer data (0-255) to the USB port at 115200 baud.

### 2. Analysis & Post-Processing (Python)
The `quantum_cleanup_save.py` script captures the data and performs the cryptographic cleanup.

**How to Run:**
1.  Capture serial output from the ESP32 into a text file named `rng_data.txt`.
2.  Run the script:
    ```bash
    python quantum_cleanup_save.py
    ```
3.  The script will:
    * Load the raw data.
    * Run statistical tests (Entropy, Chi-Square).
    * Apply SHAKE-256 processing.
    * Save the clean data to `processed_rng.txt`.
    * Print a comparative report.

##  Sample Results
Typical improvement observed after Quantum-Safe Post-Processing:

| Metric | Raw Hardware Data | Processed (SHAKE-256) | Verdict |
| :--- | :--- | :--- | :--- |
| **Shannon Entropy** | 7.92 bits | **7.999 bits** | ✅ Optimal |
| **Mean Value** | 121.5 (Biased) | **127.5 (Perfect)** | ✅ Centered |
| **Chi-Square (P)** | 0.0000 (Fail) | **0.5420 (Pass)** | ✅ Uniform |
| **NIST Monobit** | Fail | **Pass** | ✅ Random |

