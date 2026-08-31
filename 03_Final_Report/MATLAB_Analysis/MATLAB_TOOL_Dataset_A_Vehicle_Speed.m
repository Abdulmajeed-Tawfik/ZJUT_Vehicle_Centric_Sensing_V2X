%% DRIVE-BY VEHICLE SPEED ANALYSIS
% Dataset: Dataset_A_Vehicle_Speed.xlsx
%
% OUTPUTS:
% Figure 1-5  : DIRECT bridge response at x = 7 m (1x2)
% Figure 6-10 : INDIRECT drive-by response (2x3)
%
% NUMERICAL RESULTS EXPORTED TO EXCEL:
% For every acceleration signal: Peak + RMS
% For every FFT: first bridge frequency + amplitude at that frequency
%
% No summary comparison figures are generated.

clear; clc; close all;

%% USER SETTINGS
fileName = 'Dataset_A_Vehicle_Speed.xlsx';
sheetNames = {'Speed_3ms','Speed_5ms','Speed_10ms','Speed_15ms','Speed_30ms'};
speeds = [3, 5, 10, 15, 30];
bridgeLength = 15;
bridgeFreqBand = [4.5 7.0];
plotFreqMax = 35;
NFFT_min = 2^16;
saveFigures = true;
outputFolder = 'DriveBy_Speed_Results';

colTime = 'Time_s';
colRelPos = 'BridgeRelativePosition_m';
colBridge7 = 'BridgeAcc_x07m_mps2';
colSprung = 'SprungAcc_mps2';
colUnsprung = 'UnsprungAcc_mps2';
colCP = 'CPAcc_mps2';

if ~exist(outputFolder,'dir')
    mkdir(outputFolder);
end

%% PREALLOCATE RESULTS
nSpeed = numel(speeds);

Peak_B7 = zeros(nSpeed,1); RMS_B7 = zeros(nSpeed,1);
fB7 = zeros(nSpeed,1); Amp_B7 = zeros(nSpeed,1);

Peak_Sprung = zeros(nSpeed,1); RMS_Sprung = zeros(nSpeed,1);
fSprung = zeros(nSpeed,1); Amp_Sprung = zeros(nSpeed,1);

Peak_Unsprung = zeros(nSpeed,1); RMS_Unsprung = zeros(nSpeed,1);
fUnsprung = zeros(nSpeed,1); Amp_Unsprung = zeros(nSpeed,1);

Peak_CP = zeros(nSpeed,1); RMS_CP = zeros(nSpeed,1);
fCP = zeros(nSpeed,1); Amp_CP = zeros(nSpeed,1);

%% MAIN LOOP
for i = 1:nSpeed

    fprintf('\n============================================================\n');
    fprintf('Processing %s | Vehicle speed = %.1f m/s\n', sheetNames{i}, speeds(i));
    fprintf('============================================================\n');

    T = readtable(fileName,'Sheet',sheetNames{i},'VariableNamingRule','preserve');

    t = T.(colTime);
    relPos = T.(colRelPos);
    aB7 = T.(colBridge7);
    aS = T.(colSprung);
    aU = T.(colUnsprung);
    aCP = T.(colCP);

    dt = median(diff(t));
    Fs = 1/dt;

    %% Vehicle-on-bridge interval
    idxBridge = (relPos >= 0) & (relPos <= bridgeLength);
    tOn = t(idxBridge);
    tOn = tOn - tOn(1);

    aB7_on = aB7(idxBridge);
    aS_on = aS(idxBridge);
    aU_on = aU(idxBridge);
    aCP_on = aCP(idxBridge);

    %% TIME-DOMAIN METRICS
    Peak_B7(i) = max(abs(aB7_on));
    RMS_B7(i) = sqrt(mean(aB7_on.^2));

    Peak_Sprung(i) = max(abs(aS_on));
    RMS_Sprung(i) = sqrt(mean(aS_on.^2));

    Peak_Unsprung(i) = max(abs(aU_on));
    RMS_Unsprung(i) = sqrt(mean(aU_on.^2));

    Peak_CP(i) = max(abs(aCP_on));
    RMS_CP(i) = sqrt(mean(aCP_on.^2));

    %% FFT + FIRST FREQUENCY + AMPLITUDE
    % DIRECT: full bridge response
    [freq_B7, FFT_B7] = singleSidedFFT(aB7, Fs, NFFT_min);
    [fB7(i), Amp_B7(i)] = peakFrequencyAndAmplitudeInBand(freq_B7, FFT_B7, bridgeFreqBand);

    % INDIRECT: vehicle response while on bridge
    [freq_S, FFT_S] = singleSidedFFT(aS_on, Fs, NFFT_min);
    [freq_U, FFT_U] = singleSidedFFT(aU_on, Fs, NFFT_min);
    [freq_CP, FFT_CP] = singleSidedFFT(aCP_on, Fs, NFFT_min);

    [fSprung(i), Amp_Sprung(i)] = peakFrequencyAndAmplitudeInBand(freq_S, FFT_S, bridgeFreqBand);
    [fUnsprung(i), Amp_Unsprung(i)] = peakFrequencyAndAmplitudeInBand(freq_U, FFT_U, bridgeFreqBand);
    [fCP(i), Amp_CP(i)] = peakFrequencyAndAmplitudeInBand(freq_CP, FFT_CP, bridgeFreqBand);

    %% PRINT RESULTS
    fprintf('Fs = %.1f Hz\n', Fs);
    fprintf('\nDIRECT - Bridge @ 7 m\n');
    fprintf('Peak = %.6f m/s^2\n', Peak_B7(i));
    fprintf('RMS  = %.6f m/s^2\n', RMS_B7(i));
    fprintf('f1   = %.4f Hz\n', fB7(i));
    fprintf('FFT amplitude at f1 = %.6e\n', Amp_B7(i));

    fprintf('\nINDIRECT - Sprung mass\n');
    fprintf('Peak = %.6f | RMS = %.6f | f1 = %.4f Hz | Amp = %.6e\n', Peak_Sprung(i), RMS_Sprung(i), fSprung(i), Amp_Sprung(i));

    fprintf('\nINDIRECT - Unsprung mass\n');
    fprintf('Peak = %.6f | RMS = %.6f | f1 = %.4f Hz | Amp = %.6e\n', Peak_Unsprung(i), RMS_Unsprung(i), fUnsprung(i), Amp_Unsprung(i));

    fprintf('\nINDIRECT - Contact point\n');
    fprintf('Peak = %.6f | RMS = %.6f | f1 = %.4f Hz | Amp = %.6e\n', Peak_CP(i), RMS_CP(i), fCP(i), Amp_CP(i));

    %% FIGURES 1-5: DIRECT BRIDGE RESPONSE, 1x2
    figDirect = figure('Color','w','Position',[100 150 1250 470]);

    subplot(1,2,1);
    plot(tOn, aB7_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf('(a) Bridge acceleration at x = 7 m | Peak = %.3g | RMS = %.3g', Peak_B7(i), RMS_B7(i)));

    subplot(1,2,2);
    plot(freq_B7, FFT_B7, 'LineWidth',1.1);
    hold on;
    plot(fB7(i), Amp_B7(i), 'o', 'MarkerSize',7, 'LineWidth',1.2);
    xline(fB7(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf('(b) FFT | f_1 = %.2f Hz | Amp = %.3g', fB7(i), Amp_B7(i)));

    sgtitle(sprintf('Figure %d. Direct Bridge Response at %.0f m/s', i, speeds(i)));

    if saveFigures
        exportgraphics(figDirect, fullfile(outputFolder, sprintf('Figure_%02d_DIRECT_Bridge7m_%02dms.png', i, speeds(i))), 'Resolution',300);
    end

    %% FIGURES 6-10: INDIRECT VEHICLE RESPONSE, 2x3
    figIndirectNo = i + 5;
    figIndirect = figure('Color','w','Position',[80 70 1450 760]);

    subplot(2,3,1);
    plot(tOn, aS_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf('(a) Sprung acceleration | Peak=%.3g | RMS=%.3g', Peak_Sprung(i), RMS_Sprung(i)));

    subplot(2,3,2);
    plot(tOn, aU_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf('(b) Unsprung acceleration | Peak=%.3g | RMS=%.3g', Peak_Unsprung(i), RMS_Unsprung(i)));

    subplot(2,3,3);
    plot(tOn, aCP_on, 'LineWidth',1.0);
    grid on;
    xlabel('Time on bridge (s)');
    ylabel('Acceleration (m/s^2)');
    title(sprintf('(c) CP acceleration | Peak=%.3g | RMS=%.3g', Peak_CP(i), RMS_CP(i)));

    subplot(2,3,4);
    plot(freq_S, FFT_S, 'LineWidth',1.1);
    hold on;
    plot(fSprung(i), Amp_Sprung(i), 'o','MarkerSize',7,'LineWidth',1.2);
    xline(fSprung(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf('(d) Sprung FFT | f_1=%.2f Hz | Amp=%.3g', fSprung(i), Amp_Sprung(i)));

    subplot(2,3,5);
    plot(freq_U, FFT_U, 'LineWidth',1.1);
    hold on;
    plot(fUnsprung(i), Amp_Unsprung(i), 'o','MarkerSize',7,'LineWidth',1.2);
    xline(fUnsprung(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf('(e) Unsprung FFT | f_1=%.2f Hz | Amp=%.3g', fUnsprung(i), Amp_Unsprung(i)));

    subplot(2,3,6);
    plot(freq_CP, FFT_CP, 'LineWidth',1.1);
    hold on;
    plot(fCP(i), Amp_CP(i), 'o','MarkerSize',7,'LineWidth',1.2);
    xline(fCP(i),'--','LineWidth',1.0);
    xlim([0 plotFreqMax]);
    grid on;
    xlabel('Frequency (Hz)');
    ylabel('FFT amplitude');
    title(sprintf('(f) CP FFT | f_1=%.2f Hz | Amp=%.3g', fCP(i), Amp_CP(i)));

    sgtitle(sprintf('Figure %d. Indirect Drive-by Response at %.0f m/s', figIndirectNo, speeds(i)));

    if saveFigures
        exportgraphics(figIndirect, fullfile(outputFolder, sprintf('Figure_%02d_INDIRECT_Vehicle_%02dms.png', figIndirectNo, speeds(i))), 'Resolution',300);
    end
end

%% EXPORT NUMERICAL RESULTS TO EXCEL
Direct_Results = table(speeds(:), Peak_B7, RMS_B7, fB7, Amp_B7, ...
    'VariableNames', {'Speed_mps','Bridge7m_Peak_mps2','Bridge7m_RMS_mps2','Bridge7m_FirstFreq_Hz','Bridge7m_FirstFreqAmp'});

Indirect_Results = table(speeds(:), ...
    Peak_Sprung, RMS_Sprung, fSprung, Amp_Sprung, ...
    Peak_Unsprung, RMS_Unsprung, fUnsprung, Amp_Unsprung, ...
    Peak_CP, RMS_CP, fCP, Amp_CP, ...
    'VariableNames', {'Speed_mps', ...
    'Sprung_Peak_mps2','Sprung_RMS_mps2','Sprung_FirstFreq_Hz','Sprung_FirstFreqAmp', ...
    'Unsprung_Peak_mps2','Unsprung_RMS_mps2','Unsprung_FirstFreq_Hz','Unsprung_FirstFreqAmp', ...
    'CP_Peak_mps2','CP_RMS_mps2','CP_FirstFreq_Hz','CP_FirstFreqAmp'});

All_Results = outerjoin(Direct_Results, Indirect_Results, 'Keys','Speed_mps', 'MergeKeys',true);

outputExcel = fullfile(outputFolder,'DriveBy_Speed_Numerical_Results.xlsx');
if exist(outputExcel,'file')
    delete(outputExcel);
end

writetable(Direct_Results, outputExcel, 'Sheet','DIRECT_7m');
writetable(Indirect_Results, outputExcel, 'Sheet','INDIRECT');
writetable(All_Results, outputExcel, 'Sheet','ALL_RESULTS');

fprintf('\n============================================================\n');
fprintf('ANALYSIS COMPLETE\n');
fprintf('============================================================\n');
fprintf('Generated figures: Figure 1 to Figure 10 only.\n');
fprintf('Numerical results saved to:\n%s\n', outputExcel);

%% LOCAL FUNCTION 1: SINGLE-SIDED FFT
function [f, A] = singleSidedFFT(x, Fs, NFFT_min)
    x = x(:);
    good = isfinite(x);
    x = x(good);
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

%% LOCAL FUNCTION 2: FIRST FREQUENCY + AMPLITUDE IN BAND
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
