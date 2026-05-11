%% Environment Verification for NLP to Signal Processing Lab
% This script checks if your MATLAB environment is ready for the lab.

fprintf('🚀 Verifying MATLAB Environment...\n');

%% 1. Check for Signal Processing Toolbox
v = ver;
if any(strcmp({v.Name}, 'Signal Processing Toolbox'))
    fprintf('✅ Signal Processing Toolbox: FOUND\n');
else
    fprintf('❌ Signal Processing Toolbox: NOT FOUND\n');
    fprintf('   Please install it via the Add-On Explorer.\n');
end

%% 2. Check for Python Interface
try
    pyversion_info = pyenv;
    if pyversion_info.Status == "NotLoaded" || pyversion_info.Status == "Loaded"
        fprintf('✅ Python Interface: CONFIGURED (Version: %s)\n', pyversion_info.Version);
    else
         fprintf('⚠️ Python Interface: NOT CONFIGURED\n');
    end
catch
    fprintf('❌ Python Interface: ERROR accessing pyenv.\n');
end

%% 3. Check for Project Files
if exist('nlp_to_signal.m', 'file')
    fprintf('✅ Lab Scripts: FOUND\n');
else
    fprintf('❌ Lab Scripts: NOT FOUND in current directory.\n');
end

fprintf('\n🎉 Verification Complete!\n');
