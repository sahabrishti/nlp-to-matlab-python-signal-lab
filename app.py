import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import signal
from Python.nlp_logic import parse_prompt, generate_signal, generate_python_code, generate_matlab_code
import io

# Page Config
st.set_page_config(page_title="NLP Signal Studio", page_icon="📡", layout="wide")

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

# --- Sidebar ---
st.sidebar.title("🧠 NLP Input")
user_prompt = st.sidebar.text_area("What signal do you want to generate?", 
                                  "A 50Hz sine wave with 0.5 amplitude noise", height=100)

st.sidebar.subheader("🎛️ Manual Overrides")
fs = st.sidebar.slider("Sampling Rate (Hz)", 100, 10000, 2000)
duration = st.sidebar.slider("Duration (s)", 0.01, 2.0, 0.5)

st.sidebar.markdown("---")
st.sidebar.info("💡 Try: '100Hz square wave', 'linear chirp sweep to 500Hz', 'impulse response'.")

# --- Logic Processing ---
if 'code_content' not in st.session_state:
    st.session_state.code_content = ""
if 'mat_code_content' not in st.session_state:
    st.session_state.mat_code_content = ""

params = parse_prompt(user_prompt)
params['fs'] = fs
params['duration'] = duration

# Initial Code Generation (only if prompt changes)
if st.sidebar.button("✨ Regenerate from Prompt") or st.session_state.code_content == "":
    st.session_state.code_content = generate_python_code(params)
    st.session_state.mat_code_content = generate_matlab_code(params)

# --- Main Layout ---
st.title("📡 NLP to Signal Processing Studio")
st.caption("Live Code Editing | Real-time Visualization | Data Export")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("💻 Interactive Editors")
    edit_tab_py, edit_tab_mat = st.tabs(["🐍 Python Editor", "📐 MATLAB Editor"])
    
    with edit_tab_py:
        edited_code = st.text_area("Python Editor", 
                                  value=st.session_state.code_content, 
                                  height=400,
                                  label_visibility="collapsed",
                                  key="py_editor")
        if st.button("🚀 Run & Update Plot", key="run_py"):
            st.session_state.code_content = edited_code

    with edit_tab_mat:
        st.info("Note: MATLAB code editing is supported for export. Live execution requires local MATLAB engine.")
        edited_mat_code = st.text_area("MATLAB Editor", 
                                      value=st.session_state.mat_code_content, 
                                      height=350,
                                      label_visibility="collapsed",
                                      key="mat_editor")
        if st.button("💾 Save MATLAB Edits", key="save_mat"):
            st.session_state.mat_code_content = edited_mat_code

with col2:
    st.subheader("📊 Visualization")
    tab_time, tab_freq = st.tabs(["🕒 Time Domain", "🌈 Spectral Analysis"])
    
    # Execution Sandbox
    try:
        # Define a safe local scope for execution
        exec_globals = {"np": np, "signal": signal, "plt": None}
        exec(st.session_state.code_content, exec_globals)
        
        # Extract variables from sandbox
        t = exec_globals.get('t', np.linspace(0, duration, int(fs*duration)))
        sig = exec_globals.get('sig', np.zeros_like(t))
        
        with tab_time:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=t, y=sig, mode='lines', line=dict(color='#00d1ff')))
            fig.update_layout(template="plotly_dark", height=350, margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with tab_freq:
            # Simple FFT
            N = len(sig)
            xf = np.fft.rfftfreq(N, 1/fs)
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
st.subheader("📥 Export & Share")
ex_col1, ex_col2, ex_col3 = st.columns(3)

# Prepare CSV
df = pd.DataFrame({'time': t, 'amplitude': sig})
csv_data = df.to_csv(index=False).encode('utf-8')
ex_col1.download_button("💾 Download Signal (CSV)", csv_data, "signal.csv", "text/csv")

# Prepare Code
ex_col2.download_button("🐍 Download Python (.py)", st.session_state.code_content, "signal_gen.py")
ex_col3.download_button("📐 Download MATLAB (.m)", st.session_state.mat_code_content, "signal_gen.m")

# Parameter Dashboard
st.markdown("---")
st.subheader("📝 Session Metadata")
m_col1, m_col2, m_col3, m_col4 = st.columns(4)
m_col1.metric("Frequency", f"{params['freq']} Hz")
m_col2.metric("Type", params['type'].upper())
m_col3.metric("Amplitude", f"{params.get('amplitude', 1.0)} V")
m_col4.metric("Samples", len(t))
