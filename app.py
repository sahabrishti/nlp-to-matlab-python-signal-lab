import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re
from scipy import signal
from Python.nlp_logic import parse_prompt, generate_signal, generate_python_code, generate_matlab_code
import io

# Page Config
st.set_page_config(page_title="NLP Signal Studio", page_icon="S", layout="wide")

# Custom CSS for better visibility
st.markdown("""
    <style>
    .stButton>button {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    .stDownloadButton>button {
        background-color: #00d1ff !important;
        color: black !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper: Sync MATLAB code to Python parameters
def sync_matlab_params(mat_code):
    updates = {}
    patterns = {
        'freq': r'freq\s*=\s*(\d+\.?\d*)',
        'fs': r'fs\s*=\s*(\d+\.?\d*)',
        'duration': r'duration\s*=\s*(\d+\.?\d*)',
        'amplitude': r'amplitude\s*=\s*(\d+\.?\d*)'
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, mat_code)
        if match:
            updates[key] = float(match.group(1))
    return updates

# --- Sidebar ---
st.sidebar.title("NLP Input")
user_prompt = st.sidebar.text_area("What signal do you want to generate?", 
                                  "A 50Hz sine wave with 0.5 amplitude noise", height=100)

st.sidebar.subheader("Manual Overrides")
sidebar_fs = st.sidebar.slider("Sampling Rate (Hz)", 100, 10000, 2000)
sidebar_duration = st.sidebar.slider("Duration (s)", 0.01, 2.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.info("Tip: Try '100Hz square wave', 'linear chirp sweep to 500Hz', 'impulse response'.")

# --- Session State ---
if 'code_content' not in st.session_state:
    st.session_state.code_content = ""
if 'mat_code_content' not in st.session_state:
    st.session_state.mat_code_content = ""
if 'params' not in st.session_state:
    st.session_state.params = {}

# Initial Logic Processing
new_params = parse_prompt(user_prompt)
# Only update from sidebar if prompt hasn't changed or it's the first run
if st.session_state.get('last_prompt') != user_prompt:
    st.session_state.params = new_params
    st.session_state.params['fs'] = sidebar_fs
    st.session_state.params['duration'] = sidebar_duration
    st.session_state.last_prompt = user_prompt
    st.session_state.code_content = generate_python_code(st.session_state.params)
    st.session_state.mat_code_content = generate_matlab_code(st.session_state.params)

# Regenerate button
if st.sidebar.button("Regenerate from Prompt"):
    st.session_state.params = parse_prompt(user_prompt)
    st.session_state.params['fs'] = sidebar_fs
    st.session_state.params['duration'] = sidebar_duration
    st.session_state.code_content = generate_python_code(st.session_state.params)
    st.session_state.mat_code_content = generate_matlab_code(st.session_state.params)

# --- Main Layout ---
st.title("NLP to Signal Processing Studio")
st.caption("Live Code Editing | Real-time Visualization | Data Export")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Interactive Editors")
    edit_tab_py, edit_tab_mat = st.tabs(["Python Editor", "MATLAB Editor"])
    
    with edit_tab_py:
        py_editor_content = st.text_area("Python Editor Area", 
                                         value=st.session_state.code_content, 
                                         height=400,
                                         label_visibility="collapsed",
                                         key="py_editor_box")
        if st.button("Run Python & Update Plot"):
            st.session_state.code_content = py_editor_content

    with edit_tab_mat:
        st.info("Edit MATLAB parameters below and click Sync to update the Python visualization.")
        mat_editor_content = st.text_area("MATLAB Editor Area", 
                                          value=st.session_state.mat_code_content, 
                                          height=350,
                                          label_visibility="collapsed",
                                          key="mat_editor_box")
        
        m_col_save, m_col_sync = st.columns(2)
        if m_col_save.button("Save MATLAB Edits"):
            st.session_state.mat_code_content = mat_editor_content
            
        if m_col_sync.button("Sync to Python & Run"):
            # 1. Save MATLAB edits
            st.session_state.mat_code_content = mat_editor_content
            # 2. Extract params from MATLAB code
            updates = sync_matlab_params(mat_editor_content)
            # 3. Update session params and regenerate Python code
            st.session_state.params.update(updates)
            st.session_state.code_content = generate_python_code(st.session_state.params)
            st.rerun()

with col2:
    st.subheader("Visualization")
    tab_time, tab_freq = st.tabs(["Time Domain", "Spectral Analysis"])
    
    try:
        # Execution Sandbox
        exec_globals = {"np": np, "signal": signal, "plt": None}
        exec(st.session_state.code_content, exec_globals)
        
        t = exec_globals.get('t', np.linspace(0, st.session_state.params['duration'], int(st.session_state.params['fs']*st.session_state.params['duration'])))
        sig = exec_globals.get('sig', np.zeros_like(t))
        
        with tab_time:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t, y=sig, mode='lines', line=dict(color='#00d1ff')))
            fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with tab_freq:
            N = len(sig)
            fs_val = st.session_state.params.get('fs', 1000)
            xf = np.fft.rfftfreq(N, 1/fs_val)
            yf = np.abs(np.fft.rfft(sig))
            
            fig_fft = go.Figure()
            fig_fft.add_trace(go.Scatter(x=xf, y=yf, mode='lines', fill='tozeroy', line=dict(color='#ff4b4b')))
            fig_fft.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0),
                                 xaxis_title="Freq (Hz)", yaxis_title="Magnitude")
            st.plotly_chart(fig_fft, use_container_width=True)
            
    except Exception as e:
        st.error(f"Execution Error: {e}")

# --- Export Section ---
st.markdown("---")
st.subheader("Export and Share")
ex_col1, ex_col2, ex_col3 = st.columns(3)

df = pd.DataFrame({'time': t, 'amplitude': sig})
csv_data = df.to_csv(index=False).encode('utf-8')
ex_col1.download_button("Download Signal (CSV)", csv_data, "signal.csv", "text/csv")
ex_col2.download_button("Download Python (.py)", st.session_state.code_content, "signal_gen.py")
ex_col3.download_button("Download MATLAB (.m)", st.session_state.mat_code_content, "signal_gen.m")

# Parameter Dashboard
st.markdown("---")
st.subheader("Session Metadata")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Frequency", f"{st.session_state.params.get('freq', 10)} Hz")
m_col2.metric("Type", st.session_state.params.get('type', 'sine').upper())
m_col3.metric("Amplitude", f"{st.session_state.params.get('amplitude', 1.0)} V")
m_col4.metric("Samples", len(t))
