# -*- coding: utf-8 -*-
"""
DRIVE-BY BRIDGE CONDITION ANALYSIS - SPYDER / PYTHON VERSION

Dataset: Dataset_B_Bridge_Condition.xlsx

OUTPUTS
-------
Figure 1-6  : DIRECT bridge response at x = 7 m
              1 x 2 layout:
              (a) Bridge acceleration
              (b) Bridge FFT

Figure 7-12 : INDIRECT / drive-by vehicle response
              2 x 3 layout:
              Top row    : Sprung / Unsprung / CP acceleration
              Bottom row : Sprung / Unsprung / CP FFT

NUMERICAL RESULTS EXPORTED TO EXCEL
-----------------------------------
For every acceleration signal:
    - Peak acceleration
    - RMS acceleration

For every FFT:
    - First bridge frequency
    - FFT amplitude at that identified frequency

IMPORTANT
---------
- Vehicle speed is fixed at 5 m/s.
- Peak/RMS are calculated ONLY during vehicle-on-bridge interval.
- DIRECT bridge FFT uses the FULL 7 m bridge response.
- INDIRECT vehicle FFT uses ONLY vehicle-on-bridge interval.
- First bridge-frequency search band = 4.3-6.2 Hz.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =============================================================================
# USER SETTINGS
# =============================================================================
file_name = 'Dataset_B_Bridge_Condition.xlsx'

sheet_names = [
    'Damage_00pct',
    'Damage_10pct',
    'Damage_20pct',
    'Damage_30pct',
    'Damage_40pct',
    'Damage_50pct'
]

damage_levels = np.array([0, 10, 20, 30, 40, 50], dtype=float)
vehicle_speed = 5.0

bridge_length = 15.0
bridge_freq_band = (4.3, 6.2)
plot_freq_max = 35.0
nfft_min = 2**16

save_figures = True
output_folder = 'DriveBy_Bridge_Condition_Results'

# Excel column names
col_time = 'Time_s'
col_rel_pos = 'BridgeRelativePosition_m'
col_bridge7 = 'BridgeAcc_x07m_mps2'
col_sprung = 'SprungAcc_mps2'
col_unsprung = 'UnsprungAcc_mps2'
col_cp = 'CPAcc_mps2'

os.makedirs(output_folder, exist_ok=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def single_sided_fft(x, fs, nfft_minimum):
    x = np.asarray(x, dtype=float).reshape(-1)
    x = x[np.isfinite(x)]

    n = len(x)

    if n == 0:
        return np.array([]), np.array([])

    # Linear detrend
    if n > 1:
        idx = np.arange(n)
        p = np.polyfit(idx, x, 1)
        x = x - np.polyval(p, idx)

    # Hann window
    if n > 1:
        w = np.hanning(n)
    else:
        w = np.ones(1)

    xw = x * w
    coherent_gain = np.mean(w)

    nfft = max(nfft_minimum, 2**int(np.ceil(np.log2(n))))

    X = np.fft.fft(xw, n=nfft)

    A2 = np.abs(X) / (n * coherent_gain)
    half = nfft // 2 + 1
    A = A2[:half].copy()

    if len(A) > 2:
        A[1:-1] *= 2.0

    f = fs * np.arange(half) / nfft

    return f, A


def peak_frequency_and_amplitude_in_band(f, A, band):

    mask = (f >= band[0]) & (f <= band[1])

    if not np.any(mask):
        return np.nan, np.nan

    f_band = f[mask]
    A_band = A[mask]

    k = np.argmax(A_band)

    return f_band[k], A_band[k]


def rms(x):
    x = np.asarray(x, dtype=float)
    return np.sqrt(np.mean(x**2))


# =============================================================================
# READ SUMMARY SHEET
# =============================================================================
summary_input = pd.read_excel(file_name, sheet_name='Summary')
theoretical_f1 = summary_input['FirstBridgeNaturalFrequency_Hz'].to_numpy(dtype=float)


# =============================================================================
# PREALLOCATE RESULTS
# =============================================================================
n_case = len(damage_levels)

peak_b7 = np.zeros(n_case)
rms_b7 = np.zeros(n_case)
f_b7 = np.zeros(n_case)
amp_b7 = np.zeros(n_case)

peak_sprung = np.zeros(n_case)
rms_sprung = np.zeros(n_case)
f_sprung = np.zeros(n_case)
amp_sprung = np.zeros(n_case)

peak_unsprung = np.zeros(n_case)
rms_unsprung = np.zeros(n_case)
f_unsprung = np.zeros(n_case)
amp_unsprung = np.zeros(n_case)

peak_cp = np.zeros(n_case)
rms_cp = np.zeros(n_case)
f_cp = np.zeros(n_case)
amp_cp = np.zeros(n_case)


# =============================================================================
# MAIN LOOP
# =============================================================================
for i, (sheet_name, damage) in enumerate(zip(sheet_names, damage_levels)):

    print('\n' + '=' * 60)
    print(
        f'Processing {sheet_name} | Damage = {damage:.0f}% '
        f'| Speed = {vehicle_speed:.1f} m/s'
    )
    print('=' * 60)

    # Read data
    df = pd.read_excel(file_name, sheet_name=sheet_name)

    t = df[col_time].to_numpy(dtype=float)
    rel_pos = df[col_rel_pos].to_numpy(dtype=float)

    a_b7 = df[col_bridge7].to_numpy(dtype=float)
    a_s = df[col_sprung].to_numpy(dtype=float)
    a_u = df[col_unsprung].to_numpy(dtype=float)
    a_cp = df[col_cp].to_numpy(dtype=float)

    # Sampling frequency
    dt = np.median(np.diff(t))
    fs = 1.0 / dt

    # Vehicle-on-bridge interval
    idx_bridge = (rel_pos >= 0.0) & (rel_pos <= bridge_length)

    t_on = t[idx_bridge]
    t_on = t_on - t_on[0]

    a_b7_on = a_b7[idx_bridge]
    a_s_on = a_s[idx_bridge]
    a_u_on = a_u[idx_bridge]
    a_cp_on = a_cp[idx_bridge]

    # =========================================================================
    # TIME DOMAIN: PEAK + RMS
    # =========================================================================
    peak_b7[i] = np.max(np.abs(a_b7_on))
    rms_b7[i] = rms(a_b7_on)

    peak_sprung[i] = np.max(np.abs(a_s_on))
    rms_sprung[i] = rms(a_s_on)

    peak_unsprung[i] = np.max(np.abs(a_u_on))
    rms_unsprung[i] = rms(a_u_on)

    peak_cp[i] = np.max(np.abs(a_cp_on))
    rms_cp[i] = rms(a_cp_on)

    # =========================================================================
    # FFT: f1 + AMPLITUDE
    # =========================================================================

    # DIRECT - full bridge signal
    freq_b7, fft_b7 = single_sided_fft(a_b7, fs, nfft_min)

    f_b7[i], amp_b7[i] = peak_frequency_and_amplitude_in_band(
        freq_b7, fft_b7, bridge_freq_band
    )

    # INDIRECT - on-bridge only
    freq_s, fft_s = single_sided_fft(a_s_on, fs, nfft_min)
    freq_u, fft_u = single_sided_fft(a_u_on, fs, nfft_min)
    freq_cp, fft_cp = single_sided_fft(a_cp_on, fs, nfft_min)

    f_sprung[i], amp_sprung[i] = peak_frequency_and_amplitude_in_band(
        freq_s, fft_s, bridge_freq_band
    )

    f_unsprung[i], amp_unsprung[i] = peak_frequency_and_amplitude_in_band(
        freq_u, fft_u, bridge_freq_band
    )

    f_cp[i], amp_cp[i] = peak_frequency_and_amplitude_in_band(
        freq_cp, fft_cp, bridge_freq_band
    )

    # Print results
    print(f'Theoretical bridge f1 = {theoretical_f1[i]:.4f} Hz')

    print('\nDIRECT - Bridge @ 7 m')
    print(f'Peak = {peak_b7[i]:.6f} m/s²')
    print(f'RMS  = {rms_b7[i]:.6f} m/s²')
    print(f'f1   = {f_b7[i]:.4f} Hz')
    print(f'FFT amplitude at f1 = {amp_b7[i]:.6e}')

    print('\nINDIRECT - Sprung mass')
    print(
        f'Peak = {peak_sprung[i]:.6f} | RMS = {rms_sprung[i]:.6f} | '
        f'f1 = {f_sprung[i]:.4f} Hz | Amp = {amp_sprung[i]:.6e}'
    )

    print('\nINDIRECT - Unsprung mass')
    print(
        f'Peak = {peak_unsprung[i]:.6f} | RMS = {rms_unsprung[i]:.6f} | '
        f'f1 = {f_unsprung[i]:.4f} Hz | Amp = {amp_unsprung[i]:.6e}'
    )

    print('\nINDIRECT - Contact point')
    print(
        f'Peak = {peak_cp[i]:.6f} | RMS = {rms_cp[i]:.6f} | '
        f'f1 = {f_cp[i]:.4f} Hz | Amp = {amp_cp[i]:.6e}'
    )

    # =========================================================================
    # FIGURES 1-6: DIRECT
    # =========================================================================
    fig_direct_no = i + 1

    fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.7))

    axes[0].plot(t_on, a_b7_on, linewidth=1.0)
    axes[0].grid(True)
    axes[0].set_xlabel('Time on bridge (s)')
    axes[0].set_ylabel('Acceleration (m/s²)')
    axes[0].set_title(
        f'(a) Bridge acceleration at x = 7 m | Damage = {damage:.0f}%\n'
        f'Peak = {peak_b7[i]:.3g} | RMS = {rms_b7[i]:.3g}'
    )

    axes[1].plot(freq_b7, fft_b7, linewidth=1.1)
    axes[1].plot(f_b7[i], amp_b7[i], 'o', markersize=7)
    axes[1].axvline(f_b7[i], linestyle='--', linewidth=1.0)
    axes[1].set_xlim(0, plot_freq_max)
    axes[1].grid(True)
    axes[1].set_xlabel('Frequency (Hz)')
    axes[1].set_ylabel('FFT amplitude')
    axes[1].set_title(
        f'(b) FFT | Identified f₁ = {f_b7[i]:.2f} Hz | '
        f'Amp = {amp_b7[i]:.3g}\n'
        f'Theoretical f₁ = {theoretical_f1[i]:.2f} Hz'
    )

    fig.suptitle(
        f'Figure {fig_direct_no}. Direct Bridge Response - Damage {damage:.0f}%'
    )
    fig.tight_layout(rect=[0, 0, 1, 0.92])

    if save_figures:
        fig.savefig(
            os.path.join(
                output_folder,
                f'Figure_{fig_direct_no:02d}_DIRECT_Damage_{int(damage):02d}pct.png'
            ),
            dpi=300,
            bbox_inches='tight'
        )

    # =========================================================================
    # FIGURES 7-12: INDIRECT
    # =========================================================================
    fig_indirect_no = i + n_case

    fig, axes = plt.subplots(2, 3, figsize=(14.5, 7.6))

    axes[0, 0].plot(t_on, a_s_on, linewidth=1.0)
    axes[0, 0].grid(True)
    axes[0, 0].set_xlabel('Time on bridge (s)')
    axes[0, 0].set_ylabel('Acceleration (m/s²)')
    axes[0, 0].set_title(
        f'(a) Sprung acceleration\n'
        f'Peak={peak_sprung[i]:.3g} | RMS={rms_sprung[i]:.3g}'
    )

    axes[0, 1].plot(t_on, a_u_on, linewidth=1.0)
    axes[0, 1].grid(True)
    axes[0, 1].set_xlabel('Time on bridge (s)')
    axes[0, 1].set_ylabel('Acceleration (m/s²)')
    axes[0, 1].set_title(
        f'(b) Unsprung acceleration\n'
        f'Peak={peak_unsprung[i]:.3g} | RMS={rms_unsprung[i]:.3g}'
    )

    axes[0, 2].plot(t_on, a_cp_on, linewidth=1.0)
    axes[0, 2].grid(True)
    axes[0, 2].set_xlabel('Time on bridge (s)')
    axes[0, 2].set_ylabel('Acceleration (m/s²)')
    axes[0, 2].set_title(
        f'(c) CP acceleration\n'
        f'Peak={peak_cp[i]:.3g} | RMS={rms_cp[i]:.3g}'
    )

    axes[1, 0].plot(freq_s, fft_s, linewidth=1.1)
    axes[1, 0].plot(f_sprung[i], amp_sprung[i], 'o', markersize=7)
    axes[1, 0].axvline(f_sprung[i], linestyle='--', linewidth=1.0)
    axes[1, 0].set_xlim(0, plot_freq_max)
    axes[1, 0].grid(True)
    axes[1, 0].set_xlabel('Frequency (Hz)')
    axes[1, 0].set_ylabel('FFT amplitude')
    axes[1, 0].set_title(
        f'(d) Sprung FFT\n'
        f'f₁={f_sprung[i]:.2f} Hz | Amp={amp_sprung[i]:.3g}'
    )

    axes[1, 1].plot(freq_u, fft_u, linewidth=1.1)
    axes[1, 1].plot(f_unsprung[i], amp_unsprung[i], 'o', markersize=7)
    axes[1, 1].axvline(f_unsprung[i], linestyle='--', linewidth=1.0)
    axes[1, 1].set_xlim(0, plot_freq_max)
    axes[1, 1].grid(True)
    axes[1, 1].set_xlabel('Frequency (Hz)')
    axes[1, 1].set_ylabel('FFT amplitude')
    axes[1, 1].set_title(
        f'(e) Unsprung FFT\n'
        f'f₁={f_unsprung[i]:.2f} Hz | Amp={amp_unsprung[i]:.3g}'
    )

    axes[1, 2].plot(freq_cp, fft_cp, linewidth=1.1)
    axes[1, 2].plot(f_cp[i], amp_cp[i], 'o', markersize=7)
    axes[1, 2].axvline(f_cp[i], linestyle='--', linewidth=1.0)
    axes[1, 2].set_xlim(0, plot_freq_max)
    axes[1, 2].grid(True)
    axes[1, 2].set_xlabel('Frequency (Hz)')
    axes[1, 2].set_ylabel('FFT amplitude')
    axes[1, 2].set_title(
        f'(f) CP FFT\n'
        f'f₁={f_cp[i]:.2f} Hz | Amp={amp_cp[i]:.3g}'
    )

    fig.suptitle(
        f'Figure {fig_indirect_no}. Indirect Drive-by Response - '
        f'Damage {damage:.0f}%'
    )
    fig.tight_layout(rect=[0, 0, 1, 0.93])

    if save_figures:
        fig.savefig(
            os.path.join(
                output_folder,
                f'Figure_{fig_indirect_no:02d}_INDIRECT_Damage_{int(damage):02d}pct.png'
            ),
            dpi=300,
            bbox_inches='tight'
        )


# =============================================================================
# EXPORT NUMERICAL RESULTS TO EXCEL
# =============================================================================
direct_results = pd.DataFrame({
    'Damage_pct': damage_levels,
    'Theoretical_FirstFreq_Hz': theoretical_f1,
    'Bridge7m_Peak_mps2': peak_b7,
    'Bridge7m_RMS_mps2': rms_b7,
    'Bridge7m_FirstFreq_Hz': f_b7,
    'Bridge7m_FirstFreqAmp': amp_b7
})

indirect_results = pd.DataFrame({
    'Damage_pct': damage_levels,
    'Theoretical_FirstFreq_Hz': theoretical_f1,

    'Sprung_Peak_mps2': peak_sprung,
    'Sprung_RMS_mps2': rms_sprung,
    'Sprung_FirstFreq_Hz': f_sprung,
    'Sprung_FirstFreqAmp': amp_sprung,

    'Unsprung_Peak_mps2': peak_unsprung,
    'Unsprung_RMS_mps2': rms_unsprung,
    'Unsprung_FirstFreq_Hz': f_unsprung,
    'Unsprung_FirstFreqAmp': amp_unsprung,

    'CP_Peak_mps2': peak_cp,
    'CP_RMS_mps2': rms_cp,
    'CP_FirstFreq_Hz': f_cp,
    'CP_FirstFreqAmp': amp_cp
})

all_results = pd.merge(
    direct_results,
    indirect_results,
    on=['Damage_pct', 'Theoretical_FirstFreq_Hz'],
    how='outer'
)

print('\n' + '=' * 60)
print('DIRECT RESULTS')
print('=' * 60)
print(direct_results.to_string(index=False))

print('\n' + '=' * 60)
print('INDIRECT RESULTS')
print('=' * 60)
print(indirect_results.to_string(index=False))

output_excel = os.path.join(
    output_folder,
    'Bridge_Condition_Numerical_Results.xlsx'
)

with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
    direct_results.to_excel(writer, sheet_name='DIRECT_7m', index=False)
    indirect_results.to_excel(writer, sheet_name='INDIRECT', index=False)
    all_results.to_excel(writer, sheet_name='ALL_RESULTS', index=False)

print('\n' + '=' * 60)
print('ANALYSIS COMPLETE')
print('=' * 60)
print('Generated figures: Figure 1 to Figure 12 only.')
print(f'Numerical results saved to:\n{output_excel}')

plt.show()
