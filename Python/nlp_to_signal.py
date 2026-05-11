# -*- coding: utf-8 -*-
"""
NLP to Signal Processing Lab (Python)
-------------------------------------
Goal: Use NLP to generate and analyze signals.
"""

# Part 1: Signal Generation from Text
# In this section, we define a simple function that parses a natural language 
# description to generate a signal.

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import re

def text_to_signal(text, fs=1000, duration=1.0):
    """
    Simple rule-based NLP to extract frequency and type.
    """
    freq_match = re.search(r'(\d+)\s*Hz', text, re.IGNORECASE)
    freq = float(freq_match.group(1)) if freq_match else 10.0
    
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    if 'sine' in text.lower():
        sig = np.sin(2 * np.pi * freq * t)
    elif 'square' in text.lower():
        sig = signal.square(2 * np.pi * freq * t)
    else:
        sig = np.sin(2 * np.pi * freq * t)
        
    if 'noise' in text.lower():
        sig += 0.5 * np.random.randn(len(t))
        
    return t, sig

# Example usage
description = "A 50Hz square wave with noise"
t, sig = text_to_signal(description)

plt.figure(figsize=(10, 4))
plt.plot(t[:200], sig[:200])
plt.title(f"Generated Signal: {description}")
plt.grid(True)
plt.show()

# Part 2: Automated Filtering
def apply_nlp_filter(sig, fs, instruction):
    if "remove high frequency" in instruction.lower() or "low pass" in instruction.lower():
        sos = signal.butter(10, 100, 'lp', fs=fs, output='sos')
        filtered = signal.sosfilt(sos, sig)
        return filtered
    return sig

instruction = "Apply a low pass filter to remove noise"
filtered_sig = apply_nlp_filter(sig, 1000, instruction)

plt.figure(figsize=(10, 4))
plt.plot(t[:200], sig[:200], alpha=0.5, label='Original')
plt.plot(t[:200], filtered_sig[:200], label='Filtered')
plt.legend()
plt.title("NLP Controlled Filtering")
plt.show()
