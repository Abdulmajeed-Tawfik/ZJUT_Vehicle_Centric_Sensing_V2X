# -*- coding: utf-8 -*-
"""
FINAL INDIVIDUAL COURSEWORK REPORT - DATASET B
ZJUT 2026 International Summer Course | Vehicle-Centric Sensing (V2X)

Dataset B: Bridge Condition Effect

This script reproduces the numerical analysis and summary figures used in the
final report. It compares direct bridge acceleration at x = 7 m and indirect
vehicle responses (sprung mass, unsprung mass and contact point) for six bridge
condition cases.

Analysis:
- Peak absolute acceleration and RMS during vehicle-on-bridge interval
- Single-sided FFT with linear detrending, Hann window and coherent-gain
  correction
- Direct bridge FFT: full bridge signal
- Indirect vehicle FFT: vehicle-on-bridge interval only
- Bridge-frequency search band: 4.5-7.0 Hz
- Zero-padding to at least 2^16 points (for smooth display only)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

DATA_FILE = 'Dataset_B_Bridge_Condition.xlsx'
RESULT_FILE = 'Bridge_Condition_Numerical_Results.xlsx'
OUTPUT_DIR = 'Final_Report_Figures_B'

SHEETS = [
    'Damage_00pct', 'Damage_10pct', 'Damage_20pct',
    'Damage_30pct', 'Damage_40pct', 'Damage_50pct'
]
DAMAGE = np.array([0, 10, 20, 30, 40, 50], dtype=float)
BRIDGE_LENGTH = 15.0
FREQ_BAND = (4.5, 7.0)
NFFT_MIN = 2**16

COL_TIME = 'Time_s'
COL_POS = 'BridgeRelativePosition_m'
COL_BRIDGE = 'BridgeAcc_x07m_mps2'
COL_SPRUNG = 'SprungAcc_mps2'
COL_UNSPRUNG = 'UnsprungAcc_mps2'
COL_CP = 'CPAcc_mps2'


def rms(x):
    x = np.asarray(x, dtype=float)
    return np.sqrt(np.mean(x**2))


def single_sided_fft(x, fs, nfft_minimum=NFFT_MIN):
    x = np.asarray(x, dtype=float).reshape(-1)
    x = x[np.isfinite(x)]
    n = len(x)
    if n == 0:
        return np.array([]), np.array([])

    if n > 1:
        idx = np.arange(n)
        p = np.polyfit(idx, x, 1)
        x = x - np.polyval(p, idx)
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


def peak_in_band(f, A, band=FREQ_BAND):
    mask = (f >= band[0]) & (f <= band[1])
    if not np.any(mask):
        return np.nan, np.nan
    fb, Ab = f[mask], A[mask]
    k = np.argmax(Ab)
    return float(fb[k]), float(Ab[k])


def load_case(sheet):
    df = pd.read_excel(DATA_FILE, sheet_name=sheet)
    t = df[COL_TIME].to_numpy(float)
    pos = df[COL_POS].to_numpy(float)
    idx = (pos >= 0.0) & (pos <= BRIDGE_LENGTH)
    t_on = t[idx] - t[idx][0]
    return {
        'df': df,
        't': t,
        't_on': t_on,
        'idx': idx,
        'bridge_full': df[COL_BRIDGE].to_numpy(float),
        'bridge_on': df.loc[idx, COL_BRIDGE].to_numpy(float),
        'sprung_on': df.loc[idx, COL_SPRUNG].to_numpy(float),
        'unsprung_on': df.loc[idx, COL_UNSPRUNG].to_numpy(float),
        'cp_on': df.loc[idx, COL_CP].to_numpy(float),
        'fs': 1.0 / np.median(np.diff(t)),
    }


def generate_quarter_car_schematic(out_path):
    fig, ax = plt.subplots(figsize=(8.0, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    # Bridge deck and supports
    ax.plot([0.7, 9.3], [1.1, 1.1], linewidth=3)
    ax.plot([1.1, 0.7], [1.1, 0.3], linewidth=2)
    ax.plot([1.1, 1.5], [1.1, 0.3], linewidth=2)
    ax.plot([8.9, 8.5], [1.1, 0.3], linewidth=2)
    ax.plot([8.9, 9.3], [1.1, 0.3], linewidth=2)
    ax.text(5.0, 0.55, 'Bridge response $y_b(x,t)$', ha='center', fontsize=11)

    # Road profile
    xs = np.linspace(1.5, 8.5, 180)
    ys = 1.22 + 0.035*np.sin(9*xs)
    ax.plot(xs, ys, linewidth=1)
    ax.text(7.9, 1.48, 'road profile $r(x)$', fontsize=10)

    # Unsprung and sprung masses
    ax.add_patch(Rectangle((4.2, 2.2), 1.6, 0.58, fill=False, linewidth=2))
    ax.text(5.0, 2.49, 'Unsprung mass $m_u$', ha='center', va='center', fontsize=11)
    ax.add_patch(Rectangle((4.0, 5.25), 2.0, 0.72, fill=False, linewidth=2))
    ax.text(5.0, 5.61, 'Sprung mass $m_s$', ha='center', va='center', fontsize=11)

    # Suspension spring/damper
    ax.plot([4.65, 4.65], [2.78, 3.15], linewidth=1.5)
    zigx = [4.65,4.45,4.85,4.45,4.85,4.45,4.65]
    zigy = [3.15,3.45,3.75,4.05,4.35,4.65,4.95]
    ax.plot(zigx, zigy, linewidth=1.5)
    ax.text(4.05, 3.95, '$k_s$', fontsize=11)
    ax.plot([5.35,5.35], [2.78,3.5], linewidth=1.5)
    ax.add_patch(Rectangle((5.18,3.5),0.34,0.65,fill=False,linewidth=1.5))
    ax.plot([5.35,5.35],[4.15,5.25],linewidth=1.5)
    ax.text(5.62, 3.85, '$c_s$', fontsize=11)

    # Tyre spring
    ax.plot([5.0,5.0],[1.22,1.55],linewidth=1.5)
    tx=[5.0,4.8,5.2,4.8,5.2,4.8,5.0]
    ty=[1.55,1.68,1.82,1.96,2.10,2.20,2.20]
    ax.plot(tx,ty,linewidth=1.5)
    ax.text(5.28, 1.82, '$k_t$', fontsize=11)

    # Contact point and motion arrow
    ax.add_patch(Circle((5.0,1.22),0.07,fill=True))
    ax.text(5.18, 1.02, 'contact point', fontsize=10)
    ax.annotate('', xy=(7.3,6.25), xytext=(5.7,6.25), arrowprops=dict(arrowstyle='->', lw=1.8))
    ax.text(6.45, 6.45, 'vehicle speed $v$', ha='center', fontsize=11)

    ax.text(1.0, 6.35, 'Vehicle-Bridge Interaction (VBI)', fontsize=14, weight='bold')
    fig.tight_layout()
    fig.savefig(out_path, dpi=220, bbox_inches='tight')
    plt.close(fig)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    cases = [load_case(s) for s in SHEETS]
    summary = pd.read_excel(DATA_FILE, sheet_name='Summary')

    # Recompute numerical results
    rows = []
    for damage, case, (_, sm) in zip(DAMAGE, cases, summary.iterrows()):
        fs = case['fs']
        fb, Ab = single_sided_fft(case['bridge_full'], fs)
        fspr, Aspr = single_sided_fft(case['sprung_on'], fs)
        funs, Auns = single_sided_fft(case['unsprung_on'], fs)
        fcp, Acp = single_sided_fft(case['cp_on'], fs)
        bfp, bamp = peak_in_band(fb, Ab)
        sfp, samp = peak_in_band(fspr, Aspr)
        ufp, uamp = peak_in_band(funs, Auns)
        cfp, camp = peak_in_band(fcp, Acp)
        rows.append({
            'Damage_pct': damage,
            'MaximumLocalEI_Loss_pct': sm['MaximumLocalEI_Loss_pct'],
            'Theoretical_FirstFreq_Hz': sm['FirstBridgeNaturalFrequency_Hz'],
            'Bridge_Peak_mps2': np.max(np.abs(case['bridge_on'])),
            'Bridge_RMS_mps2': rms(case['bridge_on']),
            'Bridge_f1_Hz': bfp,
            'Bridge_f1_Amp': bamp,
            'Sprung_Peak_mps2': np.max(np.abs(case['sprung_on'])),
            'Sprung_RMS_mps2': rms(case['sprung_on']),
            'Sprung_f1_Hz': sfp,
            'Sprung_f1_Amp': samp,
            'Unsprung_Peak_mps2': np.max(np.abs(case['unsprung_on'])),
            'Unsprung_RMS_mps2': rms(case['unsprung_on']),
            'Unsprung_f1_Hz': ufp,
            'Unsprung_f1_Amp': uamp,
            'CP_Peak_mps2': np.max(np.abs(case['cp_on'])),
            'CP_RMS_mps2': rms(case['cp_on']),
            'CP_f1_Hz': cfp,
            'CP_f1_Amp': camp,
        })

    out = pd.DataFrame(rows)
    out.to_excel(os.path.join(OUTPUT_DIR, 'Final_Report_Dataset_B_Results.xlsx'), index=False)

    # Figure 1: own quarter-car schematic
    generate_quarter_car_schematic(os.path.join(OUTPUT_DIR, 'Figure_1_Quarter_Car_VBI.png'))

    # Figure 2: Direct time history healthy vs highest damage
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    ax.plot(cases[0]['t_on'], cases[0]['bridge_on'], label='Damage 0% (healthy)', linewidth=1.0)
    ax.plot(cases[-1]['t_on'], cases[-1]['bridge_on'], label='Damage 50%', linewidth=1.0)
    ax.set_xlabel('Time on bridge (s)')
    ax.set_ylabel('Bridge acceleration at x = 7 m (m/s$^2$)')
    ax.set_title('Direct bridge acceleration: healthy and highest damage case')
    ax.grid(True, alpha=0.35)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'Figure_2_Direct_Time_History_Healthy_vs_D50.png'), dpi=220, bbox_inches='tight')
    plt.close(fig)

    # Figure 3: Direct FFT healthy vs 50%
    fig, ax = plt.subplots(figsize=(8.5, 4.2))
    for case, label in [(cases[0], 'Damage 0% (healthy)'), (cases[-1], 'Damage 50%')]:
        f, A = single_sided_fft(case['bridge_full'], case['fs'])
        mask = (f >= 0) & (f <= 12)
        ax.plot(f[mask], A[mask], label=label, linewidth=1.2)
    ax.axvline(float(summary.iloc[0]['FirstBridgeNaturalFrequency_Hz']), linestyle='--', linewidth=1.0, label='Theoretical $f_1$, healthy')
    ax.axvline(float(summary.iloc[-1]['FirstBridgeNaturalFrequency_Hz']), linestyle=':', linewidth=1.2, label='Theoretical $f_1$, Damage 50%')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('FFT amplitude (m/s$^2$)')
    ax.set_title('Direct bridge spectrum: downward frequency shift with condition change')
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'Figure_3_Direct_FFT_Healthy_vs_D50.png'), dpi=220, bbox_inches='tight')
    plt.close(fig)

    # Figure 4: frequency trends across channels
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(DAMAGE, out['Theoretical_FirstFreq_Hz'], marker='o', label='Theoretical bridge $f_1$')
    ax.plot(DAMAGE, out['Bridge_f1_Hz'], marker='o', label='Direct bridge')
    ax.plot(DAMAGE, out['Sprung_f1_Hz'], marker='o', label='Sprung mass')
    ax.plot(DAMAGE, out['Unsprung_f1_Hz'], marker='o', label='Unsprung mass')
    ax.plot(DAMAGE, out['CP_f1_Hz'], marker='o', label='Contact point')
    ax.set_xlabel('Dataset damage parameter (%)')
    ax.set_ylabel('Identified bridge-related frequency (Hz)')
    ax.set_title('Bridge-related frequency versus bridge-condition case')
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=9, ncol=2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'Figure_4_Frequency_vs_Damage.png'), dpi=220, bbox_inches='tight')
    plt.close(fig)

    # Figure 5: RMS trends
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(DAMAGE, out['Bridge_RMS_mps2'], marker='o', label='Direct bridge')
    ax.plot(DAMAGE, out['Sprung_RMS_mps2'], marker='o', label='Sprung mass')
    ax.plot(DAMAGE, out['Unsprung_RMS_mps2'], marker='o', label='Unsprung mass')
    ax.plot(DAMAGE, out['CP_RMS_mps2'], marker='o', label='Contact point')
    ax.set_xlabel('Dataset damage parameter (%)')
    ax.set_ylabel('RMS acceleration (m/s$^2$)')
    ax.set_title('RMS response sensitivity to bridge-condition change')
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=9)
    fig.tight_layout()
    fig.savefig(os.path.join(OUTPUT_DIR, 'Figure_5_RMS_vs_Damage.png'), dpi=220, bbox_inches='tight')
    plt.close(fig)

    # Figure 6: indirect channel time histories healthy vs D50
    fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.8), sharex=True)
    channels = [
        ('sprung_on', 'Sprung-mass acceleration'),
        ('unsprung_on', 'Unsprung-mass acceleration'),
        ('cp_on', 'Contact-point acceleration'),
    ]
    for ax, (key, title) in zip(axes, channels):
        ax.plot(cases[0]['t_on'], cases[0][key], label='Damage 0%', linewidth=0.95)
        ax.plot(cases[-1]['t_on'], cases[-1][key], label='Damage 50%', linewidth=0.95)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel('Time on bridge (s)')
        ax.grid(True, alpha=0.30)
    axes[0].set_ylabel('Acceleration (m/s$^2$)')
    axes[1].legend(fontsize=8, loc='upper right')
    fig.suptitle('Indirect vehicle responses: healthy versus highest damage case', fontsize=12)
    fig.tight_layout(rect=[0,0,1,0.93])
    fig.savefig(os.path.join(OUTPUT_DIR, 'Figure_6_Indirect_Time_History_Healthy_vs_D50.png'), dpi=220, bbox_inches='tight')
    plt.close(fig)

    print(out.to_string(index=False))
    print('\nSaved report figures and results to:', OUTPUT_DIR)


if __name__ == '__main__':
    main()
