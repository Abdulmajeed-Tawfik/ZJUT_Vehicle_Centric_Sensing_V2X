%% ========================================================================
% COURSEWORK 2 - BRIDGE ACCELERATION ANALYSIS
% ZJUT 2026 International Summer Course
% Vehicle-Centric Sensing (V2X)
%
% DATA FILE:
% Benchmark_Case.xlsx
%
% This script compares bridge vertical acceleration responses at TWO
% selected bridge measurement locations.
%
% It automatically generates THREE figures:
%
%   Figure 1 - Full Acceleration Time History
%   Figure 2 - Bridge-Crossing Acceleration (Zoomed View)
%   Figure 3 - FFT Spectrum (0-50 Hz)
%
% STUDENT INSTRUCTION:
% You only need to change X1 and X2 below.
%
% Available measurement locations:
%       0, 1, 2, ..., 15 m
%
% Example:
%       X1 = 5;
%       X2 = 7;
%
% IMPORTANT:
% In your report, briefly justify WHY you selected these two locations.
%
% ========================================================================

clear;
clc;
close all;


%% ========================================================================
% 1. STUDENT INPUT
% ========================================================================
% ONLY CHANGE THESE TWO VALUES
%
% Select TWO different bridge measurement locations.
% Available locations: 0, 1, 2, ..., 15 m

X1 = 5;          % First bridge measurement location [m]
X2 = 7;          % Second bridge measurement location [m]


%% ========================================================================
% 2. FILE INFORMATION
% ========================================================================
% Keep the Excel file and this MATLAB script in the SAME folder.

filename = 'Benchmark_Case.xlsx';

sheetname = 'Benchmark';


%% ========================================================================
% 3. CHECK THE SELECTED LOCATIONS
% ========================================================================

if X1 < 0 || X1 > 15 || X1 ~= round(X1)
    error('X1 must be an integer between 0 and 15 m.');
end

if X2 < 0 || X2 > 15 || X2 ~= round(X2)
    error('X2 must be an integer between 0 and 15 m.');
end

if X1 == X2
    error('Please select TWO different bridge measurement locations.');
end


%% ========================================================================
% 4. LOAD BENCHMARK DATA
% ========================================================================
% Read the "Benchmark" worksheet from the Excel file.
%
% Important variables include:
%
%   Time_s
%   TravelDistance_m
%
% Bridge acceleration variables are named:
%
%   BridgeAcc_x00m_mps2
%   BridgeAcc_x01m_mps2
%   BridgeAcc_x02m_mps2
%   ...
%   BridgeAcc_x15m_mps2

Data = readtable(filename, ...
                 'Sheet', sheetname, ...
                 'VariableNamingRule', 'preserve');


%% ========================================================================
% 5. EXTRACT TIME AND VEHICLE TRAVEL DISTANCE
% ========================================================================

time = Data.Time_s;                       % Time [s]

travelDistance = Data.TravelDistance_m;  % Vehicle travel distance [m]


%% ========================================================================
% 6. AUTOMATICALLY SELECT THE TWO ACCELERATION SIGNALS
% ========================================================================
%
% MATLAB automatically creates the required variable names from X1 and X2.
%
% Example:
%
%       X1 = 5
%
% becomes:
%
%       BridgeAcc_x05m_mps2
%
% Therefore, students do NOT need to identify Excel column letters.

var1 = sprintf('BridgeAcc_x%02dm_mps2', X1);
var2 = sprintf('BridgeAcc_x%02dm_mps2', X2);


% Extract bridge vertical acceleration signals

acc_X1 = Data.(var1);

acc_X2 = Data.(var2);


%% ========================================================================
% 7. BENCHMARK INFORMATION
% ========================================================================
%
% Benchmark case:
%
%       Approach road = 15 m
%       Bridge        = 15 m
%       Exit road     = 15 m
%
%       Total travel distance = 45 m
%
% Vehicle speed:
%
%       v = 5 m/s
%
% Therefore:
%
%       Vehicle reaches bridge:
%
%               15 / 5 = 3 s
%
%       Vehicle leaves bridge:
%
%               30 / 5 = 6 s
%
% The vehicle is therefore physically ON THE BRIDGE between:
%
%               3 s and 6 s

bridgeEntryTime = 3;       % [s]

bridgeExitTime  = 6;       % [s]


%% ========================================================================
% 8. DISPLAY BASIC INFORMATION
% ========================================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('        COURSEWORK 2 - BRIDGE ACCELERATION ANALYSIS\n');
fprintf('============================================================\n');

fprintf('Selected Location 1 : %d m\n', X1);
fprintf('Selected Location 2 : %d m\n', X2);

fprintf('\n');

fprintf('Signal 1 : %s\n', var1);
fprintf('Signal 2 : %s\n', var2);

fprintf('\n');

fprintf('Bridge Entry : %.1f s\n', bridgeEntryTime);
fprintf('Bridge Exit  : %.1f s\n', bridgeExitTime);

fprintf('============================================================\n\n');


%% ========================================================================
% FIGURE 1
% FULL ACCELERATION TIME HISTORY
% ========================================================================
%
% PURPOSE:
%
% Compare the complete acceleration time histories at the two selected
% bridge locations.
%
% In your report, consider:
%
%   - What does the overall response look like?
%   - Are the two locations similar or different?
%   - Where do large acceleration responses occur?
%   - What happens before, during and after the vehicle crosses the bridge?
%   - Why might bridge location influence the measured response?
%
% Both signals are plotted on the SAME figure.
% A legend is automatically added.

figure('Color','w', ...
       'Position',[100 100 1100 500]);


plot(time, acc_X1, ...
     'LineWidth',1.4);

hold on;


plot(time, acc_X2, ...
     'LineWidth',1.4);


% Mark bridge entry

xline(bridgeEntryTime, '--', ...
      'Bridge Entry', ...
      'LineWidth',1.2, ...
      'LabelVerticalAlignment','bottom');


% Mark bridge exit

xline(bridgeExitTime, '--', ...
      'Bridge Exit', ...
      'LineWidth',1.2, ...
      'LabelVerticalAlignment','bottom');


xlabel('Time (s)', ...
       'FontSize',12);


ylabel('Vertical Acceleration (m/s^2)', ...
       'FontSize',12);


title('Bridge Acceleration Time History', ...
      'FontSize',15, ...
      'FontWeight','bold');


legend(sprintf('x = %d m',X1), ...
       sprintf('x = %d m',X2), ...
       'Location','best');


grid on;

box on;


set(gca, ...
    'FontSize',11, ...
    'LineWidth',1, ...
    'TickDir','out');


%% ========================================================================
% 9. SELECT BRIDGE-CROSSING DATA
% ========================================================================
%
% The benchmark vehicle is on the bridge between 3 s and 6 s.
%
% Create a logical index to extract this part of the response.

bridgeIndex = time >= bridgeEntryTime & time <= bridgeExitTime;


% Extract bridge-crossing time

time_bridge = time(bridgeIndex);


% Extract bridge-crossing acceleration signals

acc1_bridge = acc_X1(bridgeIndex);

acc2_bridge = acc_X2(bridgeIndex);


%% ========================================================================
% FIGURE 2
% BRIDGE-CROSSING ACCELERATION - ZOOMED VIEW
% ========================================================================
%
% PURPOSE:
%
% Focus only on the period when the vehicle is physically crossing
% the bridge.
%
% In your report, compare:
%
%   - Peak acceleration
%   - Overall vibration level
%   - Timing of important peaks
%   - Similarities between the two locations
%   - Differences between the two locations
%
% Do NOT simply write:
%
%       "The acceleration at Location 1 is larger."
%
% Try to explain WHY the responses may be different.

figure('Color','w', ...
       'Position',[100 100 1100 500]);


plot(time_bridge, acc1_bridge, ...
     'LineWidth',1.5);

hold on;


plot(time_bridge, acc2_bridge, ...
     'LineWidth',1.5);


xlabel('Time (s)', ...
       'FontSize',12);


ylabel('Vertical Acceleration (m/s^2)', ...
       'FontSize',12);


title('Bridge-Crossing Acceleration Response', ...
      'FontSize',15, ...
      'FontWeight','bold');


legend(sprintf('x = %d m',X1), ...
       sprintf('x = %d m',X2), ...
       'Location','best');


xlim([bridgeEntryTime bridgeExitTime]);


grid on;

box on;


set(gca, ...
    'FontSize',11, ...
    'LineWidth',1, ...
    'TickDir','out');


%% ========================================================================
% 10. CALCULATE SAMPLING INFORMATION
% ========================================================================
%
% FFT requires the sampling frequency.
%
% The sampling interval is:
%
%       dt = time between two consecutive measurements
%
% Sampling frequency is:
%
%       Fs = 1 / dt
%
% Units:
%
%       dt = seconds
%       Fs = Hz

dt = mean(diff(time));

Fs = 1/dt;


fprintf('SAMPLING INFORMATION\n');

fprintf('------------------------------------------------------------\n');

fprintf('Sampling interval dt : %.6f s\n', dt);

fprintf('Sampling frequency Fs: %.2f Hz\n', Fs);

fprintf('------------------------------------------------------------\n\n');


%% ========================================================================
% 11. PREPARE THE SIGNALS FOR FFT
% ========================================================================
%
% FFT = Fast Fourier Transform
%
% It converts the acceleration signal from:
%
%       TIME DOMAIN
%
%           Acceleration vs Time
%
% into:
%
%       FREQUENCY DOMAIN
%
%           Amplitude vs Frequency
%
%
% For this coursework, FFT is performed using the BRIDGE-CROSSING
% acceleration data (3-6 s).
%
%
% Before FFT, remove the mean value from each signal.
%
% This reduces the DC component close to 0 Hz.

acc1_fft_input = acc1_bridge - mean(acc1_bridge);

acc2_fft_input = acc2_bridge - mean(acc2_bridge);


%% ========================================================================
% 12. APPLY A HANN WINDOW
% ========================================================================
%
% The bridge-crossing signal is a finite segment of the full response.
%
% A Hann window is applied before FFT to reduce spectral leakage.
%
% Students do NOT need to derive the mathematics of the window.
%
% The important idea is:
%
%       Windowing helps produce a cleaner frequency spectrum.

N = length(acc1_fft_input);


window = hann(N);


acc1_windowed = acc1_fft_input .* window;

acc2_windowed = acc2_fft_input .* window;


%% ========================================================================
% 13. FFT - LOCATION X1
% ========================================================================

Y1 = fft(acc1_windowed);


% Correct for the amplitude reduction introduced by the Hann window

P2_1 = abs(Y1) / sum(window);


% Single-sided spectrum

P1_1 = P2_1(1:floor(N/2)+1);


% Double non-DC/non-Nyquist components

if length(P1_1) > 2

    P1_1(2:end-1) = 2*P1_1(2:end-1);

end


% Frequency vector

f = Fs*(0:floor(N/2))/N;


%% ========================================================================
% 14. FFT - LOCATION X2
% ========================================================================

Y2 = fft(acc2_windowed);


P2_2 = abs(Y2) / sum(window);


P1_2 = P2_2(1:floor(N/2)+1);


if length(P1_2) > 2

    P1_2(2:end-1) = 2*P1_2(2:end-1);

end


%% ========================================================================
% FIGURE 3
% FFT SPECTRUM - 0 TO 50 Hz
% ========================================================================
%
% PURPOSE:
%
% Compare the frequency content of the acceleration responses at
% the two selected bridge locations.
%
% The coursework focuses on:
%
%       0 - 50 Hz
%
%
% In your report:
%
%   - Identify important frequency peaks.
%   - Report their frequencies in Hz.
%   - Compare the two measurement locations.
%   - Look for peaks that appear at BOTH locations.
%   - Discuss what the peaks may represent physically.
%
%
% IMPORTANT:
%
% A frequency peak is NOT automatically a bridge natural frequency.
%
% Engineering interpretation is required.

figure('Color','w', ...
       'Position',[100 100 1100 500]);


plot(f, P1_1, ...
     'LineWidth',1.5);

hold on;


plot(f, P1_2, ...
     'LineWidth',1.5);


xlabel('Frequency (Hz)', ...
       'FontSize',12);


ylabel('Amplitude (m/s^2)', ...
       'FontSize',12);


title('FFT Spectrum of Bridge Acceleration', ...
      'FontSize',15, ...
      'FontWeight','bold');


legend(sprintf('x = %d m',X1), ...
       sprintf('x = %d m',X2), ...
       'Location','best');


% Coursework frequency range

xlim([0 50]);


grid on;

box on;


set(gca, ...
    'FontSize',11, ...
    'LineWidth',1, ...
    'TickDir','out');


%% ========================================================================
% 15. CALCULATE BASIC TIME-DOMAIN VALUES
% ========================================================================
%
% These values provide quantitative information about the two signals.
%
% PEAK ABSOLUTE ACCELERATION:
%
%       Largest absolute acceleration during bridge crossing.
%
%
% RMS:
%
%       Root Mean Square
%
%       Represents the overall vibration level.
%
%
% Students may use these values to support their discussion.

peakAcc_X1 = max(abs(acc1_bridge));

peakAcc_X2 = max(abs(acc2_bridge));


RMS_X1 = sqrt(mean(acc1_bridge.^2));

RMS_X2 = sqrt(mean(acc2_bridge.^2));


%% ========================================================================
% 16. FIND IMPORTANT FFT PEAKS
% ========================================================================
%
% Automatically identify important frequency peaks between:
%
%       0.5 Hz and 50 Hz
%
% Very low frequencies close to 0 Hz are excluded.
%
% The script identifies up to FIVE dominant peaks for each location.
%
% IMPORTANT:
%
% These peaks are provided to HELP interpretation.
%
% Students should NOT automatically label every peak as a bridge
% natural frequency.

fftRange = f >= 0.5 & f <= 50;


f_search = f(fftRange);

P1_search = P1_1(fftRange);

P2_search = P1_2(fftRange);


% Identify peaks for Location X1

[pks1, locs1] = findpeaks(P1_search, ...
                         f_search, ...
                         'SortStr','descend');


% Identify peaks for Location X2

[pks2, locs2] = findpeaks(P2_search, ...
                         f_search, ...
                         'SortStr','descend');


% Keep maximum of five peaks

nPeaks1 = min(5,length(pks1));

nPeaks2 = min(5,length(pks2));


pks1  = pks1(1:nPeaks1);

locs1 = locs1(1:nPeaks1);


pks2  = pks2(1:nPeaks2);

locs2 = locs2(1:nPeaks2);


%% ========================================================================
% 17. DISPLAY TIME-DOMAIN RESULTS
% ========================================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('            BRIDGE-CROSSING RESPONSE SUMMARY\n');
fprintf('============================================================\n');


fprintf('\nLOCATION 1: x = %d m\n', X1);

fprintf('------------------------------------------------------------\n');

fprintf('Peak absolute acceleration : %.6f m/s^2\n', peakAcc_X1);

fprintf('RMS acceleration           : %.6f m/s^2\n', RMS_X1);


fprintf('\nLOCATION 2: x = %d m\n', X2);

fprintf('------------------------------------------------------------\n');

fprintf('Peak absolute acceleration : %.6f m/s^2\n', peakAcc_X2);

fprintf('RMS acceleration           : %.6f m/s^2\n', RMS_X2);


fprintf('\n============================================================\n');


%% ========================================================================
% 18. DISPLAY IMPORTANT FFT PEAKS
% ========================================================================

fprintf('\n');
fprintf('============================================================\n');
fprintf('                 IMPORTANT FFT PEAKS\n');
fprintf('============================================================\n');


fprintf('\nLocation x = %d m\n', X1);

fprintf('------------------------------------------------------------\n');

for i = 1:nPeaks1

    fprintf('Peak %d : %8.3f Hz   Amplitude = %.6f m/s^2\n', ...
            i, locs1(i), pks1(i));

end


fprintf('\nLocation x = %d m\n', X2);

fprintf('------------------------------------------------------------\n');

for i = 1:nPeaks2

    fprintf('Peak %d : %8.3f Hz   Amplitude = %.6f m/s^2\n', ...
            i, locs2(i), pks2(i));

end


fprintf('\n============================================================\n');


%% ========================================================================
% 19. FINAL COURSEWORK REMINDER
% ========================================================================
%
% Your coursework report should NOT simply contain three figures.
%
% For each figure:
%
%
%       1. DESCRIBE
%
%          What does the figure show?
%
%
%       2. COMPARE
%
%          How are the two bridge locations similar or different?
%
%
%       3. QUANTIFY
%
%          Support your observations using numerical values where
%          appropriate.
%
%          Examples:
%
%               Peak acceleration
%               RMS acceleration
%               Frequency peaks
%
%
%       4. INTERPRET
%
%          Explain WHY the behaviour may occur from an engineering
%          perspective.
%
%
% ========================================================================
%
% SUGGESTED TWO-PAGE REPORT STRUCTURE
% ========================================================================
%
%
% PAGE 1 - TIME-DOMAIN ANALYSIS
%
%   Selected Measurement Locations
%
%       - State X1 and X2
%       - Briefly justify your choices
%
%
%   Figure 1
%
%       Full Acceleration Time History
%
%
%   Figure 2
%
%       Bridge-Crossing Acceleration Response
%
%
%   Discussion
%
%       - Describe
%       - Compare
%       - Quantify
%       - Interpret
%
%
% ------------------------------------------------------------------------
%
% PAGE 2 - FREQUENCY-DOMAIN ANALYSIS
%
%   Figure 3
%
%       FFT Spectrum (0-50 Hz)
%
%
%   FFT Results
%
%       - Identify important frequency peaks
%       - Report frequencies in Hz
%       - Compare the two locations
%
%
%   Engineering Interpretation
%
%       - What do the results tell you?
%       - Why might the responses differ?
%       - What might the important frequency peaks represent?
%
%
%   Conclusion
%
%       - Summarise 2-3 key findings
%
%
% ========================================================================
%
% REMEMBER:
%
%       GOOD ANALYSIS IS NOT ABOUT PRODUCING MORE FIGURES.
%
%       GOOD ANALYSIS =
%
%       CLEAR FIGURES
%              +
%       QUANTITATIVE COMPARISON
%              +
%       ENGINEERING INTERPRETATION
%
% ========================================================================
% END OF SCRIPT
% ========================================================================