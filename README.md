# NLP to MATLAB and Python Signal Processing Lab

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MATLAB R2023b+](https://img.shields.io/badge/MATLAB-R2023b+-orange.svg)](https://www.mathworks.com/products/matlab.html)

![Lab Header](assets/header.png)

A hands-on workshop focused on bridging the gap between Natural Language Processing (NLP) and Digital Signal Processing (DSP). Learn how to leverage modern LLMs and NLP techniques to automate signal generation, filtering, and analysis in both Python and MATLAB.

---

## Quick Start (One-Click Setup)

To set up the Python environment and verify MATLAB dependencies, run the appropriate command for your OS:

### Windows
```powershell
.\setup.ps1
```

### macOS / Linux
```bash
chmod +x setup.sh
./setup.sh
```

---

## Interactive Console

We have included a web-based console where you can input prompts and interactively view the results.

### To Launch:
```powershell
.\.venv\Scripts\streamlit run app.py
```

**Features:**
- Natural Language Input: Describe your signal in plain English.
- Real-time Visualization: Interactive plots using Plotly.
- Export Options: Download generated code (.py/.m) and signal data (.csv).

---

## Overview

In this lab, you will explore how to:
1. Translate Text to Signals: Convert natural language descriptions into executable signal processing parameters.
2. AI-Assisted Code Generation: Use LLMs (Large Language Models) to generate robust DSP code.
3. Cross-Platform Integration: Compare workflows in Python (SciPy/NumPy) and MATLAB (Signal Processing Toolbox).
4. Hybrid Workflows: Run Python-based NLP models directly within MATLAB.

---

## Prerequisites

### For Python
- Python 3.8 or higher.
- Libraries: numpy, scipy, matplotlib, transformers.
- Install via: pip install -r Python/requirements.txt

### For MATLAB
- MATLAB R2023b or later recommended.
- Signal Processing Toolbox.
- (Optional) Python Interface configured in MATLAB.

---

## Repository Structure

```bash
├── MATLAB/
│   └── nlp_to_signal.m      # MATLAB script for NLP-DSP workflows
├── Python/
│   ├── nlp_to_signal.py     # Interactive Lab Script
│   └── requirements.txt     # Python dependencies
└── assets/                  # Documentation images and diagrams
```

---

## Lab Modules

### 1. Python: The NLP Powerhouse
- Objective: Use the transformers library to extract signal features from text.
- Task: Create a function that takes "A 10Hz sine wave with Gaussian noise" and returns a cleaned signal plot.

### 2. MATLAB: The DSP Industry Standard
- Objective: Implement text-to-code using MATLAB's AI Chat Playground or custom prompt engineering.
- Task: Design a Butterworth filter by describing its characteristics in plain English.

### 3. The Bridge: Calling Python NLP from MATLAB
- Objective: Use MATLAB's pyrun to leverage advanced NLP models for MATLAB signal variables.

---

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements.

---

*Developed for the NLP & Signal Processing Workshop Series.*
