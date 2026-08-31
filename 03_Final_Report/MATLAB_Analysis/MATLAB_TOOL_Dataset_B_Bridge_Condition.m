%% DRIVE-BY BRIDGE CONDITION ANALYSIS
% Dataset: Dataset_B_Bridge_Condition.xlsx
%
% OUTPUTS:
%   Figure 1-6  : DIRECT bridge response at x = 7 m
%                 1 x 2 layout:
%                 (a) Bridge acceleration
%                 (b) Bridge FFT
%
%   Figure 7-12 : INDIRECT / drive-by vehicle response
%                 2 x 3 layout:
%                 Top row    : Sprung / Unsprung / CP acceleration
%                 Bottom row : Sprung / Unsprung / CP FFT
%
% NUMERICAL RESULTS EXPORTED TO EXCEL:
%   For every acceleration signal:
%       - Peak acceleration
%       - RMS acceleration
%
%   For every FFT:
%       - First bridge frequency
%       - FFT amplitude at that identified frequency
%
% IMPORTANT:
% - Vehicle speed is fixed at 5 m/s.
% - Peak/RMS are calculated ONLY during the vehicle-on-bridge interval.
% - DIRECT bridge FFT uses the FULL 7 m bridge response.
% - INDIRECT vehicle FFT uses ONLY the vehicle-on-bridge interval.
% - First bridge-frequency search band = 4.3-6.2 Hz.
%   This covers the expected f1 shift from healthy to 50% damage.
% - Zero-padding smooths the FFT curve but does NOT improve true resolution.

clear; clc; close all;

%% ------------------------------------------------------------------------
% USER SETTINGS
% -------------------------------------------------------------------------
fileName = 'Dataset_B_Bridge_Condition.xlsx';

sheetNames = {'Damage_00pct','Damage_10pct','Damage_20pct', ...
              'Damage_30pct','Damage_40pct','Damage_50pct'};

damageLevels = [0, 10, 20, 30, 40, 50];     % damage parameter (%)
vehicleSpeed = 5;                            % m/s

bridgeLength   = 15;                         % m
bridgeFreqBand = [4.3 6.2];                 % Hz
plotFreqMax    = 35;                         % Hz
NFFT_min       = 2^16;

saveFigures  = true;
outputFolder = 'DriveBy_Bridge_Condition_Results';

% Dataset column names
colTime      = 'Time_s';
colRelPos    = 'BridgeRelativePosition_m';
colBridge7   = 'BridgeAcc_x07m_mps2';
colSprung    = 'SprungAcc_mps2';
colUnsprung  = 'UnsprungAcc_mps2';
colCP        = 'CPAcc_mps2';

if ~exist(outputFolder,'dir')
    mkdir(outputFolder);
end

%% ------------------------------------------------------------------------
% READ SUMMARY SHEET
% -------------------------------------------------------------------------
SummaryInput = readtable(fileName, 'Sheet','Summary', ...
    'VariableNamingRule','preserve');

theoretical_f1 = SummaryInput.FirstBridgeNaturalFrequency_Hz;

%% ------------------------------------------------------------------------
% PREALLOCATE RESULTS
% -------------------------------------------------------------------------
nCase = numel(damageLevels);

% DIRECT
Peak_B7 = zeros(nCase,1);
RMS_B7  = zeros(nCase,1);
fB7     = zeros(nCase,1);
Amp_B7  = zeros(nCase,1);

% INDIRECT
Peak_Sprung = zeros(nCase,1);
RMS_Sprung  = zeros(nCase,1);
fSprung     = zeros(nCase,1);
Amp_Sprung  = zeros(nCase,1);

Peak_Unsprung = zeros(nCase,1);
RMS_Unsprung  = zeros(nCase,1);
fUnsprung     = zeros(nCase,1);
Amp_Unsprung  = zeros(nCase,1);

Peak_CP = zeros(nCase,1);
RMS_CP  = zeros(nCase,1);
fCP     = zeros(nCase,1);
Amp_CP  = zeros(nCase,1);

%% ------------------------------------------------------------------------
% MAIN LOOP
% -------------------------------------------------------------------------
for i = 1:nCase

    fprintf('\n============================================================\n');
    fprintf('Processing %s | Damage = %.0f%% | Speed = %.1f m/s\n', ...
        sheetNames{i}, damageLevels(i), vehicleSpeed);
    fprintf('============================================================\n');

    %% Read data
    T = readtable(fileName, ...
        'Sheet',sheetNames{i}, ...
        'VariableNamingRule','preserve');

    t      = T.(colTime);
    relPos = T.(colRelPos);

    aB7 = T.(colBridge7);
    aS  = T.(colSprung);
    aU  = T.(colUnsprung);
    aCP = T.(colCP);

    %% Sampling frequency
    dt = median(diff(t));
    Fs = 1/dt;

    %% Vehicle-on-bridge interval
    idxBridge = (relPos >= 0) & (relPos <= bridgeLength);

    tOn = t(idxBridge);
    tOn = tOn - tOn(1);

    aB7_on = aB7(idxBridge);
    aS_on  = aS(idxBridge);
    aU_on  = aU(idxBridge);
    aCP_on = aCP(idxBridge);

    %% ====================================================================
    % TIME-DOMAIN METRICS: PEAK + RMS
    % =====================================================================
    Peak_B7(i) = max(abs(aB7_on));
    RMS_B7(i)  = sqrt(mean(aB7_on.^2));

    Peak_Sprung(i) = max(abs(aS_on));
    RMS_Sprung(i)  = sqrt(mean(aS_on.^2));

    Peak_Unsprung(i) = max(abs(aU_on));
    RMS_Unsprung(i)  = sqrt(mean(aU_on.^2));

    Peak_CP(i) = max(abs(aCP_on));
    RMS_CP(i)  = sqrt(mean(aCP_on.^2));

    %% ====================================================================
    % FFT + FIRST BRIDGE FREQUENCY + AMPLITUDE
    % =====================================================================

    % DIRECT bridge FFT - full signal
    [freq_B7, FFT_B7] = singleSidedFFT(aB7, Fs, NFFT_min);

    [fB7(i), Amp_B7(i)] = peakFrequencyAndAmplitudeInBand( ...
        freq_B7, FFT_B7, bridgeFreqBand);

    % INDIRECT FFTs - vehicle-on-bridge only
    [freq_S, FFT_S]   = singleSidedFFT(aS_on,  Fs, NFFT_min);
    [freq_U, FFT_U]   = singleSidedFFT(aU_on,  Fs, NFFT_min);
    [freq_CP, FFT_CP] = singleSidedFFT(aCP_on, Fs, NFFT_min);

    [fSprung(i), Amp_Sprung(i)] = peakFrequencyAndAmplitudeInBand( ...
        freq_S, FFT_S, bridgeFreqBand);

    [fUnsprung(i), Amp_Unsprung(i)] = peakFrequencyAndAmplitudeInBand( ...
        freq_U, FFT_U, bridgeFreqBand);

    [fCP(i), Amp_CP(i)] = peakFrequencyAndAmplitudeInBand( ...
        freq_CP, FFT_CP, bridgeFreqBand);

    %% Print results
    fprintf('Theoretical bridge f1 = %.4f Hz\n', theoretical_f1(i));

    fprintf('\nDIRECT - Bridge @ 7 m\n');
    fprintf('Peak = %.6f m/s^2\n', Peak_B7(i));
    fprintf('RMS  = %.6f m/s^2\n', RMS_B7(i));
    fprintf('f1   = %.4f Hz\n', fB7(i));
    fprintf('FFT amplitude at f1 = %.6e\n', Amp_B7(i));

    fprintf('\nINDIRECT - Sprung mass\n');
    fprintf('Peak = %.6f | RMS = %.6f | f1 = %.4f Hz | Amp = %.6e\n', ...
        Peak_Sprung(i), RMS_Sprung(i), fSprung(i), Amp_Sprung(i));

    fprintf('\nINDIRECT - Unsprung mass\n');
    fprintf('Peak = %.6f | RMS = %.6f | f1 = %.4f Hz | Amp = %.6e\n', ...
        Peak_Unsprung(i), RMS_Unsprung(i), fUnsprung(i), Amp_Unsprung(i));

    fprintf('\nINDIRECT - Contact point\n');
    fprintf('Peak = %.6f | RMS = %.6f | f1 = %.4f Hz | Amp = %.6e\n', ...
        Peak_CP(i), RMS_CP(i), fCP(i), Amp_CP(i));

    %% ====================================================================
    % FIGURES 1-6: DIRECT BRIDGE RESPONSE
    % =====================================================================
    figDirect = figure( ...
        'Color','w', ...
        'Name',sprintf('Direct Bridge Response - Damage %.0f%%',damageLevels(i)), ...
        'Position',[100 150 1250 470]);

    subplot(1,2,1);
    plot(tOn, aB7_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf(['(a) Bridge acceleration at x = 7 m | Damage = %.0f%%\n' ...
                   'Peak = %.3g | RMS = %.3g'], ...
        damageLevels(i), Peak_B7(i), RMS_B7(i)));

    subplot(1,2,2);
    plot(freq_B7, FFT_B7, 'LineWidth',1.1);
    hold on;
    plot(fB7(i), Amp_B7(i), 'o', 'MarkerSize',7, 'LineWidth',1.2);
    xline(fB7(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf(['(b) FFT | Identified f_1 = %.2f Hz | Amp = %.3g\n' ...
                   'Theoretical f_1 = %.2f Hz'], ...
        fB7(i), Amp_B7(i), theoretical_f1(i)));

    sgtitle(sprintf('Figure %d. Direct Bridge Response - Damage %.0f%%', ...
        i, damageLevels(i)));

    if saveFigures
        exportgraphics(figDirect, ...
            fullfile(outputFolder, ...
            sprintf('Figure_%02d_DIRECT_Damage_%02dpct.png', ...
            i, damageLevels(i))), ...
            'Resolution',300);
    end

    %% ====================================================================
    % FIGURES 7-12: INDIRECT / DRIVE-BY VEHICLE RESPONSE
    % =====================================================================
    figIndirectNo = i + nCase;

    figIndirect = figure( ...
        'Color','w', ...
        'Name',sprintf('Indirect Response - Damage %.0f%%',damageLevels(i)), ...
        'Position',[80 70 1450 760]);

    subplot(2,3,1);
    plot(tOn, aS_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf('(a) Sprung acceleration\nPeak=%.3g | RMS=%.3g', ...
        Peak_Sprung(i), RMS_Sprung(i)));

    subplot(2,3,2);
    plot(tOn, aU_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf('(b) Unsprung acceleration\nPeak=%.3g | RMS=%.3g', ...
        Peak_Unsprung(i), RMS_Unsprung(i)));

    subplot(2,3,3);
    plot(tOn, aCP_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf('(c) CP acceleration\nPeak=%.3g | RMS=%.3g', ...
        Peak_CP(i), RMS_CP(i)));

    subplot(2,3,4);
    plot(freq_S, FFT_S, 'LineWidth',1.1);
    hold on;
    plot(fSprung(i), Amp_Sprung(i), 'o', 'MarkerSize',7);
    xline(fSprung(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf('(d) Sprung FFT\nf_1=%.2f Hz | Amp=%.3g', ...
        fSprung(i), Amp_Sprung(i)));

    subplot(2,3,5);
    plot(freq_U, FFT_U, 'LineWidth',1.1);
    hold on;
    plot(fUnsprung(i), Amp_Unsprung(i), 'o', 'MarkerSize',7);
    xline(fUnsprung(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf('(e) Unsprung FFT\nf_1=%.2f Hz | Amp=%.3g', ...
        fUnsprung(i), Amp_Unsprung(i)));

    subplot(2,3,6);
    plot(freq_CP, FFT_CP, 'LineWidth',1.1);
    hold on;
    plot(fCP(i), Amp_CP(i), 'o', 'MarkerSize',7);
    xline(fCP(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf('(f) CP FFT\nf_1=%.2f Hz | Amp=%.3g', ...
        fCP(i), Amp_CP(i)));

    sgtitle(sprintf('Figure %d. Indirect Drive-by Response - Damage %.0f%%', ...
        figIndirectNo, damageLevels(i)));

    if saveFigures
        exportgraphics(figIndirect, ...
            fullfile(outputFolder, ...
            sprintf('Figure_%02d_INDIRECT_Damage_%02dpct.png', ...
            figIndirectNo, damageLevels(i))), ...
            'Resolution',300);
    end
end

%% ------------------------------------------------------------------------
% EXPORT RESULTS TO EXCEL
% -------------------------------------------------------------------------
Direct_Results = table( ...
    damageLevels(:), ...
    theoretical_f1, ...
    Peak_B7, RMS_B7, fB7, Amp_B7, ...
    'VariableNames', { ...
    'Damage_pct', ...
    'Theoretical_FirstFreq_Hz', ...
    'Bridge7m_Peak_mps2', ...
    'Bridge7m_RMS_mps2', ...
    'Bridge7m_FirstFreq_Hz', ...
    'Bridge7m_FirstFreqAmp'});

Indirect_Results = table( ...
    damageLevels(:), ...
    theoretical_f1, ...
    Peak_Sprung, RMS_Sprung, fSprung, Amp_Sprung, ...
    Peak_Unsprung, RMS_Unsprung, fUnsprung, Amp_Unsprung, ...
    Peak_CP, RMS_CP, fCP, Amp_CP, ...
    'VariableNames', { ...
    'Damage_pct', ...
    'Theoretical_FirstFreq_Hz', ...
    'Sprung_Peak_mps2', ...
    'Sprung_RMS_mps2', ...
    'Sprung_FirstFreq_Hz', ...
    'Sprung_FirstFreqAmp', ...
    'Unsprung_Peak_mps2', ...
    'Unsprung_RMS_mps2', ...
    'Unsprung_FirstFreq_Hz', ...
    'Unsprung_FirstFreqAmp', ...
    'CP_Peak_mps2', ...
    'CP_RMS_mps2', ...
    'CP_FirstFreq_Hz', ...
    'CP_FirstFreqAmp'});

All_Results = outerjoin(Direct_Results, Indirect_Results, ...
    'Keys',{'Damage_pct','Theoretical_FirstFreq_Hz'}, ...
    'MergeKeys',true);

disp(' ');
disp('================ DIRECT RESULTS ================');
disp(Direct_Results);

disp(' ');
disp('================ INDIRECT RESULTS ================');
disp(Indirect_Results);

outputExcel = fullfile(outputFolder, ...
    'Bridge_Condition_Numerical_Results.xlsx');

if exist(outputExcel,'file')
    delete(outputExcel);
end

writetable(Direct_Results, outputExcel, 'Sheet','DIRECT_7m');
writetable(Indirect_Results, outputExcel, 'Sheet','INDIRECT');
writetable(All_Results, outputExcel, 'Sheet','ALL_RESULTS');

fprintf('\n============================================================\n');
fprintf('ANALYSIS COMPLETE\n');
fprintf('============================================================\n');
fprintf('Generated figures: Figure 1 to Figure 12 only.\n');
fprintf('Numerical results saved to:\n%s\n', outputExcel);

%% ========================================================================
% LOCAL FUNCTION 1: SINGLE-SIDED FFT
% ========================================================================
function [f, A] = singleSidedFFT(x, Fs, NFFT_min)

    x = x(:);
    x = x(isfinite(x));
    x = detrend(x,'linear');

    N = length(x);

    if N > 1
        n = (0:N-1)';
        w = 0.5 - 0.5*cos(2*pi*n/(N-1));
    else
        w = 1;
    end

    xw = x .* w;
    coherentGain = mean(w);

    NFFT = max(NFFT_min, 2^nextpow2(N));

    X = fft(xw, NFFT);

    A2 = abs(X) / (N * coherentGain);
    A = A2(1:floor(NFFT/2)+1);

    if length(A) > 2
        A(2:end-1) = 2*A(2:end-1);
    end

    f = Fs*(0:floor(NFFT/2))'/NFFT;
end

%% ========================================================================
% LOCAL FUNCTION 2: FIND f1 + FFT AMPLITUDE
% ========================================================================
function [fPeak, ampPeak] = peakFrequencyAndAmplitudeInBand(f, A, band)

    idx = (f >= band(1)) & (f <= band(2));

    if ~any(idx)
        fPeak = NaN;
        ampPeak = NaN;
        return;
    end

    fBand = f(idx);
    ABand = A(idx);

    [ampPeak, k] = max(ABand);
    fPeak = fBand(k);
end
