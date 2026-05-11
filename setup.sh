#!/bin/bash

echo -e "\033[0;36m🚀 Starting Local Setup for NLP to Signal Processing Lab...\033[0m"

# 1. Check for Python
if command -v python3 &>/dev/null; then
    echo -e "\033[0;32m✅ Python found.\033[0m"
else
    echo -e "\033[0;31m❌ Python 3 not found. Please install Python 3.8+.\033[0m"
    exit 1
fi

# 2. Create Virtual Environment
echo -e "\033[0;33m📦 Creating virtual environment (.venv)...\033[0m"
python3 -m venv .venv

# 3. Activate and Install Dependencies
echo -e "\033[0;33m📥 Installing Python dependencies from Python/requirements.txt...\033[0m"
./.venv/bin/pip install -r Python/requirements.txt

if [ $? -eq 0 ]; then
    echo -e "\033[0;32m✅ Python setup complete!\033[0m"
else
    echo -e "\033[0;31m❌ Failed to install dependencies.\033[0m"
    exit 1
fi

# 4. MATLAB Instructions
echo ""
echo -e "\033[0;36m🛠️ MATLAB Setup:\033[0m"
echo "1. Open MATLAB."
echo "2. Navigate to the 'MATLAB' folder in this repository."
echo "3. Run 'check_env.m' to verify your toolboxes."

echo ""
echo -e "\033[0;32m🎉 Setup finished successfully!\033[0m"
echo "To start the Python lab, run: ./.venv/bin/python Python/nlp_to_signal.py"
