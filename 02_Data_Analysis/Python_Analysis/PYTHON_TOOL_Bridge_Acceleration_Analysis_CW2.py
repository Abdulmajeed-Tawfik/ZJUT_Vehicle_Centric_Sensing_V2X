# ============================================================================
# COURSEWORK 2 - BRIDGE ACCELERATION ANALYSIS
# ZJUT 2026 International Summer Course
# Vehicle-Centric Sensing (V2X)
#
# PYTHON VERSION
#
# DATA FILE:
# Benchmark_Case.xlsx
#
# This script compares bridge vertical acceleration responses at TWO
# selected bridge measurement locations.
#
# It automatically generates THREE figures:
#
#   Figure 1 - Full Acceleration Time History
#   Figure 2 - Bridge-Crossing Acceleration (Zoomed View)
#   Figure 3 - FFT Spectrum (0-50 Hz)
#
# STUDENT INSTRUCTION:
# You only need to change X1 and X2 below.
#
# Available measurement locations:
#       0, 1, 2, ..., 15 m
#
# Example:
#       X1 = 5
#       X2 = 7
#
# IMPORTANT:
# In your report, briefly justify WHY you selected these two locations.
#
# ============================================================================


# ============================================================================
# 0. IMPORT PYTHON PACKAGES
# ============================================================================

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.signal import find_peaks
from scipy.signal.windows import hann


# ============================================================================
# 1. STUDENT INPUT
# ============================================================================
# ONLY CHANGE THESE TWO VALUES
#
# Select TWO different bridge measurement locations.
# Available locations: 0, 1, 2, ..., 15 m

X1 = 5          # First bridge measurement location [m]
X2 = 7          # Second bridge measurement location [m]


# ============================================================================
# 2. FILE INFORMATION
# ============================================================================
# Keep the Excel file and this Python script in the SAME folder.

filename = 'Benchmark_Case.xlsx'

sheetname = 'Benchmark'


# ============================================================================
# 3. CHECK THE SELECTED LOCATIONS
# ============================================================================

if not isinstance(X1, (int, np.integer)) or X1 < 0 or X1 > 15:
    raise ValueError('X1 must be an integer between 0 and 15 m.')

if not isinstance(X2, (int, np.integer)) or X2 < 0 or X2 > 15:
    raise ValueError('X2 must be an integer between 0 and 15 m.')

if X1 == X2:
    raise ValueError('Please select TWO different bridge measurement locations.')


# ============================================================================
# 4. LOAD BENCHMARK DATA
# ============================================================================
# Read the "Benchmark" worksheet from the Excel file.
#
# Important variables include:
#
#   Time_s
#   TravelDistance_m
#
# Bridge acceleration variables are named:
#
#   BridgeAcc_x00m_mps2
#   BridgeAcc_x01m_mps2
#   BridgeAcc_x02m_mps2
#   ...
#   BridgeAcc_x15m_mps2

Data = pd.read_excel(
    filename,
    sheet_name=sheetname,
    engine='openpyxl'
)


# ============================================================================
# 5. EXTRACT TIME AND VEHICLE TRAVEL DISTANCE
# ============================================================================

time = Data['Time_s'].to_numpy()

travelDistance = Data['TravelDistance_m'].to_numpy()


# ============================================================================
# 6. AUTOMATICALLY SELECT THE TWO ACCELERATION SIGNALS
# ============================================================================
#
# Python automatically creates the required variable names from X1 and X2.
#
# Example:
#
#       X1 = 5
#
# becomes:
#
#       BridgeAcc_x05m_mps2
#
# Therefore, students do NOT need to identify Excel column letters.

var1 = f'BridgeAcc_x{X1:02d}m_mps2'
var2 = f'BridgeAcc_x{X2:02d}m_mps2'


# Check that the required columns exist

if var1 not in Data.columns:
    raise KeyError(f'Cannot find "{var1}" in the Excel file.')

if var2 not in Data.columns:
    raise KeyError(f'Cannot find "{var2}" in the Excel file.')


# Extract bridge vertical acceleration signals

acc_X1 = Data[var1].to_numpy()

acc_X2 = Data[var2].to_numpy()


# ============================================================================
# 7. BENCHMARK INFORMATION
# ============================================================================
#
# Benchmark case:
#
#       Approach road = 15 m
#       Bridge        = 15 m
#       Exit road     = 15 m
#
#       Total travel distance = 45 m
#
# Vehicle speed:
#
#       v = 5 m/s
#
# Therefore:
#
#       Vehicle reaches bridge:
#
#               15 / 5 = 3 s
#
#       Vehicle leaves bridge:
#
#               30 / 5 = 6 s
#
# The vehicle is therefore physically ON THE BRIDGE between:
#
#               3 s and 6 s

bridgeEntryTime = 3.0       # [s]

bridgeExitTime = 6.0        # [s]


# ============================================================================
# 8. DISPLAY BASIC INFORMATION
# ============================================================================

print()
print('============================================================')
print('        COURSEWORK 2 - BRIDGE ACCELERATION ANALYSIS')
print('============================================================')

print(f'Selected Location 1 : {X1} m')
print(f'Selected Location 2 : {X2} m')

print()

print(f'Signal 1 : {var1}')
print(f'Signal 2 : {var2}')

print()

print(f'Bridge Entry : {bridgeEntryTime:.1f} s')
print(f'Bridge Exit  : {bridgeExitTime:.1f} s')

print('============================================================')
print()


# ============================================================================
# FIGURE 1
# FULL ACCELERATION TIME HISTORY
# ============================================================================
#
# PURPOSE:
#
# Compare the complete acceleration time histories at the two selected
# bridge locations.
#
# In your report, consider:
#
#   - What does the overall response look like?
#   - Are the two locations similar or different?
#   - Where do large acceleration responses occur?
#   - What happens before, during and after the vehicle crosses the bridge?
#   - Why might bridge location influence the measured response?
#
# Both signals are plotted on the SAME figure.
# A legend is automatically added.

plt.figure(figsize=(11, 5))

plt.plot(
    time,
    acc_X1,
    linewidth=1.4,
    label=f'x = {X1} m'
)

plt.plot(
    time,
    acc_X2,
    linewidth=1.4,
    label=f'x = {X2} m'
)


# Mark bridge entry

plt.axvline(
    bridgeEntryTime,
    linestyle='--',
    linewidth=1.2
)

plt.text(
    bridgeEntryTime,
    plt.ylim()[1],
    ' Bridge Entry',
    verticalalignment='top'
)


# Mark bridge exit

plt.axvline(
    bridgeExitTime,
    linestyle='--',
    linewidth=1.2
)

plt.text(
    bridgeExitTime,
    plt.ylim()[1],
    ' Bridge Exit',
    verticalalignment='top'
)


plt.xlabel('Time (s)', fontsize=12)

plt.ylabel('Vertical Acceleration (m/s²)', fontsize=12)

plt.title(
    'Bridge Acceleration Time History',
    fontsize=15,
    fontweight='bold'
)

plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================================
# 9. SELECT BRIDGE-CROSSING DATA
# ============================================================================
#
# The benchmark vehicle is on the bridge between 3 s and 6 s.
#
# Create an index to extract this part of the response.

bridgeIndex = (
    (time >= bridgeEntryTime) &
    (time <= bridgeExitTime)
)


# Extract bridge-crossing time

time_bridge = time[bridgeIndex]


# Extract bridge-crossing acceleration signals

acc1_bridge = acc_X1[bridgeIndex]

acc2_bridge = acc_X2[bridgeIndex]


# ============================================================================
# FIGURE 2
# BRIDGE-CROSSING ACCELERATION - ZOOMED VIEW
# ============================================================================
#
# PURPOSE:
#
# Focus only on the period when the vehicle is physically crossing
# the bridge.
#
# In your report, compare:
#
#   - Peak acceleration
#   - Overall vibration level
#   - Timing of important peaks
#   - Similarities between the two locations
#   - Differences between the two locations
#
# Do NOT simply write:
#
#       "The acceleration at Location 1 is larger."
#
# Try to explain WHY the responses may be different.

plt.figure(figsize=(11, 5))


plt.plot(
    time_bridge,
    acc1_bridge,
    linewidth=1.5,
    label=f'x = {X1} m'
)


plt.plot(
    time_bridge,
    acc2_bridge,
    linewidth=1.5,
    label=f'x = {X2} m'
)


plt.xlabel(
    'Time (s)',
    fontsize=12
)


plt.ylabel(
    'Vertical Acceleration (m/s²)',
    fontsize=12
)


plt.title(
    'Bridge-Crossing Acceleration Response',
    fontsize=15,
    fontweight='bold'
)


plt.xlim(
    bridgeEntryTime,
    bridgeExitTime
)


plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================================
# 10. CALCULATE SAMPLING INFORMATION
# ============================================================================
#
# FFT requires the sampling frequency.
#
# The sampling interval is:
#
#       dt = time between two consecutive measurements
#
# Sampling frequency is:
#
#       Fs = 1 / dt
#
# Units:
#
#       dt = seconds
#       Fs = Hz

dt = np.mean(np.diff(time))

Fs = 1.0 / dt


print('SAMPLING INFORMATION')

print('------------------------------------------------------------')

print(f'Sampling interval dt : {dt:.6f} s')

print(f'Sampling frequency Fs: {Fs:.2f} Hz')

print('------------------------------------------------------------')
print()


# ============================================================================
# 11. PREPARE THE SIGNALS FOR FFT
# ============================================================================
#
# FFT = Fast Fourier Transform
#
# It converts the acceleration signal from:
#
#       TIME DOMAIN
#
#           Acceleration vs Time
#
# into:
#
#       FREQUENCY DOMAIN
#
#           Amplitude vs Frequency
#
#
# For this coursework, FFT is performed using the BRIDGE-CROSSING
# acceleration data (3-6 s).
#
#
# Before FFT, remove the mean value from each signal.
#
# This reduces the DC component close to 0 Hz.

acc1_fft_input = acc1_bridge - np.mean(acc1_bridge)

acc2_fft_input = acc2_bridge - np.mean(acc2_bridge)


# ============================================================================
# 12. APPLY A HANN WINDOW
# ============================================================================
#
# The bridge-crossing signal is a finite segment of the full response.
#
# A Hann window is applied before FFT to reduce spectral leakage.
#
# Students do NOT need to derive the mathematics of the window.
#
# The important idea is:
#
#       Windowing helps produce a cleaner frequency spectrum.

N = len(acc1_fft_input)


window = hann(N)


acc1_windowed = acc1_fft_input * window

acc2_windowed = acc2_fft_input * window


# ============================================================================
# 13. FFT - LOCATION X1
# ============================================================================

Y1 = np.fft.fft(acc1_windowed)


# Correct for the amplitude reduction introduced by the Hann window

P2_1 = np.abs(Y1) / np.sum(window)


# Single-sided spectrum

P1_1 = P2_1[:N // 2 + 1].copy()


# Double non-DC/non-Nyquist components

if len(P1_1) > 2:

    P1_1[1:-1] = 2 * P1_1[1:-1]


# Frequency vector

f = Fs * np.arange(0, N // 2 + 1) / N


# ============================================================================
# 14. FFT - LOCATION X2
# ============================================================================

Y2 = np.fft.fft(acc2_windowed)


P2_2 = np.abs(Y2) / np.sum(window)


P1_2 = P2_2[:N // 2 + 1].copy()


if len(P1_2) > 2:

    P1_2[1:-1] = 2 * P1_2[1:-1]


# ============================================================================
# FIGURE 3
# FFT SPECTRUM - 0 TO 50 Hz
# ============================================================================
#
# PURPOSE:
#
# Compare the frequency content of the acceleration responses at
# the two selected bridge locations.
#
# The coursework focuses on:
#
#       0 - 50 Hz
#
#
# In your report:
#
#   - Identify important frequency peaks.
#   - Report their frequencies in Hz.
#   - Compare the two measurement locations.
#   - Look for peaks that appear at BOTH locations.
#   - Discuss what the peaks may represent physically.
#
#
# IMPORTANT:
#
# A frequency peak is NOT automatically a bridge natural frequency.
#
# Engineering interpretation is required.

plt.figure(figsize=(11, 5))


plt.plot(
    f,
    P1_1,
    linewidth=1.5,
    label=f'x = {X1} m'
)


plt.plot(
    f,
    P1_2,
    linewidth=1.5,
    label=f'x = {X2} m'
)


plt.xlabel(
    'Frequency (Hz)',
    fontsize=12
)


plt.ylabel(
    'Amplitude (m/s²)',
    fontsize=12
)


plt.title(
    'FFT Spectrum of Bridge Acceleration',
    fontsize=15,
    fontweight='bold'
)


# Coursework frequency range

plt.xlim(0, 50)


plt.legend()

plt.grid(True)

plt.tight_layout()

plt.show()


# ============================================================================
# 15. CALCULATE BASIC TIME-DOMAIN VALUES
# ============================================================================
#
# These values provide quantitative information about the two signals.
#
# PEAK ABSOLUTE ACCELERATION:
#
#       Largest absolute acceleration during bridge crossing.
#
#
# RMS:
#
#       Root Mean Square
#
#       Represents the overall vibration level.
#
#
# Students may use these values to support their discussion.

peakAcc_X1 = np.max(np.abs(acc1_bridge))

peakAcc_X2 = np.max(np.abs(acc2_bridge))


RMS_X1 = np.sqrt(np.mean(acc1_bridge ** 2))

RMS_X2 = np.sqrt(np.mean(acc2_bridge ** 2))


# ============================================================================
# 16. FIND IMPORTANT FFT PEAKS
# ============================================================================
#
# Automatically identify important frequency peaks between:
#
#       0.5 Hz and 50 Hz
#
# Very low frequencies close to 0 Hz are excluded.
#
# The script identifies up to FIVE dominant peaks for each location.
#
# IMPORTANT:
#
# These peaks are provided to HELP interpretation.
#
# Students should NOT automatically label every peak as a bridge
# natural frequency.

fftRange = (
    (f >= 0.5) &
    (f <= 50)
)


f_search = f[fftRange]

P1_search = P1_1[fftRange]

P2_search = P1_2[fftRange]


# --------------------------------------------------------------------------
# Identify peaks for Location X1
# --------------------------------------------------------------------------

peak_indices1, _ = find_peaks(P1_search)


pks1 = P1_search[peak_indices1]

locs1 = f_search[peak_indices1]


# Sort peaks from largest amplitude to smallest amplitude

sort_index1 = np.argsort(pks1)[::-1]


pks1 = pks1[sort_index1]

locs1 = locs1[sort_index1]


# --------------------------------------------------------------------------
# Identify peaks for Location X2
# --------------------------------------------------------------------------

peak_indices2, _ = find_peaks(P2_search)


pks2 = P2_search[peak_indices2]

locs2 = f_search[peak_indices2]


# Sort peaks from largest amplitude to smallest amplitude

sort_index2 = np.argsort(pks2)[::-1]


pks2 = pks2[sort_index2]

locs2 = locs2[sort_index2]


# --------------------------------------------------------------------------
# Keep maximum of five peaks
# --------------------------------------------------------------------------

nPeaks1 = min(5, len(pks1))

nPeaks2 = min(5, len(pks2))


pks1 = pks1[:nPeaks1]

locs1 = locs1[:nPeaks1]


pks2 = pks2[:nPeaks2]

locs2 = locs2[:nPeaks2]


# ============================================================================
# 17. DISPLAY TIME-DOMAIN RESULTS
# ============================================================================

print()
print('============================================================')
print('            BRIDGE-CROSSING RESPONSE SUMMARY')
print('============================================================')


print(f'\nLOCATION 1: x = {X1} m')

print('------------------------------------------------------------')

print(
    f'Peak absolute acceleration : '
    f'{peakAcc_X1:.6f} m/s²'
)

print(
    f'RMS acceleration           : '
    f'{RMS_X1:.6f} m/s²'
)


print(f'\nLOCATION 2: x = {X2} m')

print('------------------------------------------------------------')

print(
    f'Peak absolute acceleration : '
    f'{peakAcc_X2:.6f} m/s²'
)

print(
    f'RMS acceleration           : '
    f'{RMS_X2:.6f} m/s²'
)


print()
print('============================================================')


# ============================================================================
# 18. DISPLAY IMPORTANT FFT PEAKS
# ============================================================================

print()
print('============================================================')
print('                 IMPORTANT FFT PEAKS')
print('============================================================')


print(f'\nLocation x = {X1} m')

print('------------------------------------------------------------')


for i in range(nPeaks1):

    print(
        f'Peak {i + 1} : '
        f'{locs1[i]:8.3f} Hz   '
        f'Amplitude = {pks1[i]:.6f} m/s²'
    )


print(f'\nLocation x = {X2} m')

print('------------------------------------------------------------')


for i in range(nPeaks2):

    print(
        f'Peak {i + 1} : '
        f'{locs2[i]:8.3f} Hz   '
        f'Amplitude = {pks2[i]:.6f} m/s²'
    )


print()
print('============================================================')


# ============================================================================
# 19. FINAL COURSEWORK REMINDER
# ============================================================================
#
# Your coursework report should NOT simply contain three figures.
#
# For each figure:
#
#
#       1. DESCRIBE
#
#          What does the figure show?
#
#
#       2. COMPARE
#
#          How are the two bridge locations similar or different?
#
#
#       3. QUANTIFY
#
#          Support your observations using numerical values where
#          appropriate.
#
#          Examples:
#
#               Peak acceleration
#               RMS acceleration
#               Frequency peaks
#
#
#       4. INTERPRET
#
#          Explain WHY the behaviour may occur from an engineering
#          perspective.
#
#
# ============================================================================
#
# SUGGESTED TWO-PAGE REPORT STRUCTURE
# ============================================================================
#
#
# PAGE 1 - TIME-DOMAIN ANALYSIS
#
#   Selected Measurement Locations
#
#       - State X1 and X2
#       - Briefly justify your choices
#
#
#   Figure 1
#
#       Full Acceleration Time History
#
#
#   Figure 2
#
#       Bridge-Crossing Acceleration Response
#
#
#   Discussion
#
#       - Describe
#       - Compare
#       - Quantify
#       - Interpret
#
#
# --------------------------------------------------------------------------
#
# PAGE 2 - FREQUENCY-DOMAIN ANALYSIS
#
#   Figure 3
#
#       FFT Spectrum (0-50 Hz)
#
#
#   FFT Results
#
#       - Identify important frequency peaks
#       - Report frequencies in Hz
#       - Compare the two locations
#
#
#   Engineering Interpretation
#
#       - What do the results tell you?
#       - Why might the responses differ?
#       - What might the important frequency peaks represent?
#
#
#   Conclusion
#
#       - Summarise 2-3 key findings
#
#
# ============================================================================
#
# REMEMBER:
#
#       GOOD ANALYSIS IS NOT ABOUT PRODUCING MORE FIGURES.
#
#       GOOD ANALYSIS =
#
#       CLEAR FIGURES
#              +
#       QUANTITATIVE COMPARISON
#              +
#       ENGINEERING INTERPRETATION
#
# ============================================================================
# END OF SCRIPT
# ============================================================================