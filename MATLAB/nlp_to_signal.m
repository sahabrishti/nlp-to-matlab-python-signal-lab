%% NLP to Signal Processing Lab (MATLAB)
% Goal: Explore MATLAB's capabilities in NLP-driven Signal Processing.

%% Part 1: Basic Signal Synthesis from Description
description = "50Hz sine wave with 0.2 amplitude noise";

freq = 50; 
fs = 1000;
t = 0:1/fs:1-1/fs;

if contains(description, 'sine', 'IgnoreCase', true)
    sig = sin(2*pi*freq*t);
end

if contains(description, 'noise', 'IgnoreCase', true)
    sig = sig + 0.2*randn(size(t));
end

figure;
plot(t(1:200), sig(1:200));
title(['Generated: ', description]);
grid on;

%% Part 2: Interactive Filtering with Signal Analyzer
instruction = "low pass filter at 100Hz";

if contains(instruction, 'low pass')
    [b, a] = butter(6, 100/(fs/2));
    filteredSig = filter(b, a, sig);
end

hold on;
plot(t(1:200), filteredSig(1:200), 'LineWidth', 1.5);
legend('Original', 'Filtered');
title('NLP-Based Filtering in MATLAB');

%% Part 3: Bridge to Python NLP
try
    pyRegex = py.importlib.import_module('re');
    match = pyRegex.search('(\d+)Hz', description);
    extractedFreq = char(match.group(py.int(1)));
    fprintf('Extracted Frequency via Python NLP: %s Hz\n', extractedFreq);
catch
    disp('Python not configured or library missing. Skipping bridge example.');
end
