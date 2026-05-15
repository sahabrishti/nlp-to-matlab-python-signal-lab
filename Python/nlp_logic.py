import numpy as np
import re
from scipy import signal

class SignalProcessor:
    """Handles NLP parsing and signal generation logic."""
    
    DEFAULT_PARAMS = {
        'freq': 10.0, 'type': 'sine', 'noise': 0.0, 'fs': 2000, 
        'duration': 0.5, 'amplitude': 1.0, 'detect_peaks': False,
        'filter': None, 'bass_boost': 0, 'bpm': 60
    }

    @staticmethod
    def parse(prompt, current=None):
        params = (current or SignalProcessor.DEFAULT_PARAMS).copy()
        text = prompt.lower()

        # 🤖 Rule-Based NLU (Fallback)
        freq_match = re.search(r'(\d+\.?\d*)\s*hz', text)
        bpm_match = re.search(r'(\d+)\s*bpm', text)
        amp_match = re.search(r'(\d+\.?\d*)\s*(amp|v)', text)
        is_relative = any(x in text for x in ['increase', 'decrease', 'more', 'less', 'higher', 'lower'])
        
        if freq_match:
            val = float(freq_match.group(1))
            if is_relative and 'freq' in text:
                params['freq'] += val if any(x in text for x in ['increase', 'more', 'higher']) else -val
                params['freq'] = max(0.1, params['freq'])
            else:
                params['freq'] = val

        if bpm_match:
            params['bpm'] = int(bpm_match.group(1))

        if amp_match:
            val = float(amp_match.group(1))
            if is_relative and 'amp' in text:
                params['amplitude'] += val if any(x in text for x in ['increase', 'more']) else -val
                params['amplitude'] = max(0.1, params['amplitude'])
            else:
                params['amplitude'] = val

        for stype in ['sine', 'square', 'sawtooth', 'chirp', 'impulse', 'ecg']:
            if stype in text:
                params['type'] = stype

        if 'noise' in text:
            params['noise'] = 0.0 if 'remove' in text else 0.5
            
        params['detect_peaks'] = 'peak' in text or 'detect' in text or 'hrv' in text
        
        if 'low pass' in text or 'lp' in text:
            params['filter'] = 'compare' if 'high pass' in text or 'hp' in text or 'compare' in text else 'lp'
        elif 'high pass' in text or 'hp' in text:
            params['filter'] = 'hp'

        if 'bass' in text:
            params['bass_boost'] = 10 if any(x in text for x in ['boost', 'increase']) else 0
            
        return params

def generate_python_source(p):
    """Generates clean, idiomatic Python code for signal generation."""
    lines = [
        "import numpy as np",
        "from scipy import signal",
        f"fs, dur = {p['fs']}, {p['duration']}",
        f"t = np.linspace(0, dur, int(fs * dur), endpoint=False)",
        f"f, amp = {p['freq']}, {p['amplitude']}"
    ]

    if p['type'] == 'ecg':
        lines.append(f"def get_ecg(t_arr, bpm={p['bpm']}):")
        lines.append("    sig = np.zeros_like(t_arr); period = 60/bpm")
        lines.append("    for s in np.arange(0, t_arr[-1], period):")
        lines.append("        sig += 1.0 * np.exp(-((t_arr-(s+0.1))**2)/(2*0.005**2))") # QRS
        lines.append("        sig += 0.15 * np.exp(-((t_arr-(s+0.02))**2)/(2*0.015**2))") # P
        lines.append("        sig += 0.25 * np.exp(-((t_arr-(s+0.3))**2)/(2*0.035**2))") # T
        lines.append("    return sig")
        lines.append("sig = amp * get_ecg(t)")
    elif p['type'] == 'chirp':
        lines.append(f"sig = amp * signal.chirp(t, f0=10, f1=f, t1=dur, method='linear')")
    elif p['type'] == 'impulse':
        lines.append("sig = np.zeros_like(t); sig[0] = amp")
    elif p['type'] == 'square':
        lines.append("sig = amp * signal.square(2 * np.pi * f * t)")
    elif p['type'] == 'sawtooth':
        lines.append("sig = amp * signal.sawtooth(2 * np.pi * f * t)")
    else:
        lines.append("sig = amp * np.sin(2 * np.pi * f * t)")

    if p['noise'] > 0:
        lines.append(f"sig += {p['noise']} * np.random.randn(len(t))")

    if p['filter']:
        lines.append("nyq = 0.5 * fs")
        if p['filter'] in ['lp', 'compare']:
            lines.append("b, a = signal.butter(4, 100/nyq, 'low')")
            lines.append("sig_lp = signal.filtfilt(b, a, sig)")
        if p['filter'] in ['hp', 'compare']:
            lines.append("b, a = signal.butter(4, 100/nyq, 'high')")
            lines.append("sig_hp = signal.filtfilt(b, a, sig)")

    if p['bass_boost'] > 0:
        lines.append(f"b, a = signal.butter(2, 200/(0.5*fs), 'low')")
        lines.append(f"sig += (10**({p['bass_boost']}/20)-1) * signal.filtfilt(b, a, sig)")

    # 🏥 Automated Peak Detection & HRV Metrics
    if p['detect_peaks']:
        lines.append("peaks, _ = signal.find_peaks(sig, height=np.max(sig)*0.5, distance=int(fs*0.1))")
        if p['type'] == 'ecg':
            lines.append("rr_intervals = np.diff(t[peaks]) * 1000") # in ms
            lines.append("hrv_sdnn = np.std(rr_intervals) if len(rr_intervals) > 0 else 0")
            lines.append("bpm_actual = 60000 / np.mean(rr_intervals) if len(rr_intervals) > 0 else 0")
    else:
        lines.append("peaks = None")

    return "\n".join(lines)

def generate_matlab_source(p):
    """Equivalent MATLAB source generator."""
    lines = [f"fs = {p['fs']}; t = 0:1/fs:{p['duration']}-1/fs;", f"f = {p['freq']}; amp = {p['amplitude']};"]
    if p['type'] == 'sine': lines.append("sig = amp * sin(2*pi*f*t);")
    else: lines.append(f"sig = amp * {p['type']}(2*pi*f*t);")
    if p['noise'] > 0: lines.append(f"sig = sig + {p['noise']}*randn(size(t));")
    if p['detect_peaks']: lines.append("[pks, locs] = findpeaks(sig, 'MinPeakHeight', max(sig)*0.5);")
    lines.append("plot(t, sig); grid on;")
    return "\n".join(lines)
