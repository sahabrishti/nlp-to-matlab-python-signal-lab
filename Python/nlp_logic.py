import numpy as np
import re
from scipy import signal

def parse_prompt(prompt):
    """
    Extract parameters from natural language prompt.
    """
    params = {
        'freq': 10.0,
        'type': 'sine',
        'noise': 0.0,
        'fs': 1000,
        'duration': 1.0,
        'amplitude': 1.0
    }
    
    # Frequency
    freq_match = re.search(r'(\d+)\s*Hz', prompt, re.IGNORECASE)
    if freq_match:
        params['freq'] = float(freq_match.group(1))
        
    # Amplitude
    amp_match = re.search(r'(\d+\.?\d*)\s*(amp|amplitude|v)', prompt, re.IGNORECASE)
    if amp_match:
        params['amplitude'] = float(amp_match.group(1))

    # Signal Type
    if 'square' in prompt.lower():
        params['type'] = 'square'
    elif 'sawtooth' in prompt.lower():
        params['type'] = 'sawtooth'
    elif 'chirp' in prompt.lower() or 'sweep' in prompt.lower():
        params['type'] = 'chirp'
    elif 'impulse' in prompt.lower():
        params['type'] = 'impulse'
        
    # Noise
    if 'noise' in prompt.lower():
        params['noise'] = 0.5
        
    return params

def generate_signal(params):
    t = np.linspace(0, params['duration'], int(params['fs'] * params['duration']), endpoint=False)
    
    if params['type'] == 'sine':
        sig = params['amplitude'] * np.sin(2 * np.pi * params['freq'] * t)
    elif params['type'] == 'square':
        sig = params['amplitude'] * signal.square(2 * np.pi * params['freq'] * t)
    elif params['type'] == 'sawtooth':
        sig = params['amplitude'] * signal.sawtooth(2 * np.pi * params['freq'] * t)
    elif params['type'] == 'chirp':
        sig = params['amplitude'] * signal.chirp(t, f0=10, f1=params['freq'], t1=params['duration'], method='linear')
    elif params['type'] == 'impulse':
        sig = np.zeros_like(t)
        sig[0] = params['amplitude']
    else:
        sig = params['amplitude'] * np.sin(2 * np.pi * params['freq'] * t)
        
    if params['noise'] > 0:
        sig += params['noise'] * np.random.randn(len(t))
        
    return t, sig

def generate_python_code(params):
    return f"""import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

fs = {params['fs']}
t = np.linspace(0, {params['duration']}, int(fs * {params['duration']}), endpoint=False)
freq = {params['freq']}

# Generate {params['type']} wave
{"sig = np.sin(2 * np.pi * freq * t)" if params['type'] == 'sine' else f"sig = signal.{params['type']}(2 * np.pi * freq * t)"}

{"# Add noise\nsig += 0.5 * np.random.randn(len(t))" if params['noise'] > 0 else ""}

plt.plot(t, sig)
plt.show()
"""

def generate_matlab_code(params):
    return f"""fs = {params['fs']};
t = 0:1/fs:{params['duration']}-1/fs;
freq = {params['freq']};

% Generate {params['type']} wave
{"sig = sin(2*pi*freq*t);" if params['type'] == 'sine' else f"sig = {params['type']}(2*pi*freq*t);"}

{"% Add noise\nsig = sig + 0.5*randn(size(t));" if params['noise'] > 0 else ""}

plot(t, sig);
grid on;
"""
