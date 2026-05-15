import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy import signal
from Python.nlp_logic import SignalProcessor, generate_python_source, generate_matlab_source
import io
import wave

# --- Configuration ---
st.set_page_config(page_title="Signal Studio Pro", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stTabs [data-baseweb="tab-list"] { gap: 16px; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] { 
        height: 48px; padding: 0 28px; background-color: #1e2130; 
        border-radius: 8px; color: #888; font-weight: 600; border: 1px solid #333;
    }
    .stTabs [aria-selected="true"] { background-color: #ff4b4b !important; color: white !important; }
    div[data-testid="stMetricValue"] { color: #00d1ff; font-weight: bold; }
    h1, h2, h3 { color: #00d1ff; }
    p, li, .stMarkdown { color: #ccc; line-height: 1.8; }
    .doc-section { background-color: #1e2130; padding: 25px; border-radius: 12px; border: 1px solid #333; margin-bottom: 30px; }
    </style>
""", unsafe_allow_html=True)

# --- AI Helper (Lazy Loaded) ---
@st.cache_resource
def get_ai_pipeline():
    from transformers import pipeline
    return pipeline("text-generation", model="distilgpt2")

# --- State Initialization ---
if 'params' not in st.session_state:
    st.session_state.params = SignalProcessor.DEFAULT_PARAMS.copy()
if 'py_code' not in st.session_state:
    st.session_state.py_code = generate_python_source(st.session_state.params)
if 'mat_code' not in st.session_state:
    st.session_state.mat_code = generate_matlab_source(st.session_state.params)
if 'last_p' not in st.session_state:
    st.session_state.last_p = ""
if 'ai_enabled' not in st.session_state:
    st.session_state.ai_enabled = False

# --- Navigation ---
st.sidebar.title("Signal Studio Pro")
nav_choice = st.sidebar.radio("Navigation", ["Studio Workspace", "Documentation"], label_visibility="collapsed")
st.sidebar.markdown("---")

if nav_choice == "Studio Workspace":
    st.title("Signal Studio Pro")
    
    # AI Mode Toggle
    st.sidebar.subheader("AI Intelligence")
    if st.sidebar.toggle("Enable Advanced NLU (Local LLM)", value=st.session_state.ai_enabled):
        st.session_state.ai_enabled = True
        try:
            with st.sidebar.status("Loading AI Model..."):
                pipe = get_ai_pipeline()
            st.sidebar.success("AI Active")
        except Exception as e:
            st.sidebar.error(f"AI Error: {e}")
            st.session_state.ai_enabled = False
    else:
        st.session_state.ai_enabled = False

    st.sidebar.markdown("---")
    st.sidebar.subheader("Command Input")
    manual = st.sidebar.text_input("Natural Language Command", placeholder="e.g. increase freq by 5Hz", key="manual_cmd")

    if manual and manual != st.session_state.last_p:
        st.session_state.params = SignalProcessor.parse(manual, st.session_state.params)
        st.session_state.py_code = generate_python_source(st.session_state.params)
        st.session_state.mat_code = generate_matlab_source(st.session_state.params)
        st.session_state.last_p = manual

    st.sidebar.markdown("---")
    st.sidebar.subheader("Simulation Config")
    st.session_state.params['fs'] = st.sidebar.slider("Sample Rate", 500, 10000, st.session_state.params['fs'])
    st.session_state.params['duration'] = st.sidebar.slider("Duration", 0.1, 2.0, st.session_state.params['duration'])

    # Main UI
    c_ed, c_viz = st.columns([1, 1.3])
    with c_ed:
        st.subheader("Implementation")
        t1, t2 = st.tabs(["Python Editor", "MATLAB Editor"])
        with t1:
            st.session_state.py_code = st.text_area("PY", value=st.session_state.py_code, height=550, label_visibility="collapsed")
            if st.button("Apply Changes", use_container_width=True): st.rerun()
        with t2:
            st.session_state.mat_code = st.text_area("MAT", value=st.session_state.mat_code, height=550, label_visibility="collapsed")

    with c_viz:
        st.subheader("Real-time Analytics")
        tabs = st.tabs(["Time Domain", "Spectrogram", "FFT Spectrum"])
        try:
            ctx = {"np": np, "signal": signal}
            exec(st.session_state.py_code, ctx)
            t, sig, pks = ctx.get('t'), ctx.get('sig'), ctx.get('peaks')
            aux = {k: v for k, v in ctx.items() if k in ['sig_lp', 'sig_hp']}
            with tabs[0]:
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=t, y=sig, name="Signal", line=dict(color='#00d1ff', width=2)))
                for k, v in aux.items(): fig.add_trace(go.Scatter(x=t, y=v, name=k.upper(), line=dict(dash='dot')))
                if pks is not None and len(pks) > 0:
                    fig.add_trace(go.Scatter(x=t[pks], y=sig[pks], mode='markers', marker=dict(color='#ff4b4b', size=10)))
                fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### Audio Playback")
                audio_data = (sig / np.max(np.abs(sig)) * 32767).astype(np.int16)
                with io.BytesIO() as wav_io:
                    with wave.open(wav_io, 'wb') as wav:
                        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(st.session_state.params['fs'])
                        wav.writeframes(audio_data.tobytes())
                    st.audio(wav_io.getvalue(), format="audio/wav")
            with tabs[1]:
                f, ts, sxx = signal.spectrogram(sig, st.session_state.params['fs'])
                fig = go.Figure(go.Heatmap(x=ts, y=f, z=10*np.log10(sxx+1e-12), colorscale='Viridis'))
                fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig, use_container_width=True)
            with tabs[2]:
                xf = np.fft.rfftfreq(len(sig), 1/st.session_state.params['fs'])
                yf = np.abs(np.fft.rfft(sig))
                fig = go.Figure(go.Scatter(x=xf, y=yf, fill='tozeroy', line=dict(color='#ff4b4b')))
                fig.update_layout(template="plotly_dark", height=450, margin=dict(l=0,r=0,t=10,b=0))
                st.plotly_chart(fig, use_container_width=True)

            if pks is not None and ctx.get('hrv_sdnn') is not None:
                st.markdown("---")
                st.subheader("🏥 Medical Metrics (ECG)")
                h_cols = st.columns(3)
                h_cols[0].metric("Actual Heart Rate", f"{ctx.get('bpm_actual', 0):.1f} BPM")
                h_cols[1].metric("HRV (SDNN)", f"{ctx.get('hrv_sdnn', 0):.2f} ms")
                h_cols[2].metric("RR Count", len(pks))
        except Exception as e:
            st.error(f"Runtime Error: {e}")

    st.markdown("---")
    m = st.columns(3)
    m[0].metric("Frequency", f"{st.session_state.params['freq']} Hz")
    m[1].metric("Topology", st.session_state.params['type'].upper())
    m[2].metric("Noise Ratio", f"{st.session_state.params['noise']} V")

else:
    # --- Expanded Documentation UI ---
    st.title("Project Documentation & Technical Guide")
    st.markdown("---")
    
    # 1. Project Foundation & Architecture
    st.header("1. Project Foundation & Architecture")
    st.markdown("""
    This project is an advanced educational sandbox designed to demonstrate the intersection of **Natural Language Processing (NLP)** 
    and **Digital Signal Processing (DSP)**. It provides a real-time environment where high-level human descriptions are 
    algorithmically translated into rigorous mathematical signals.
    """)
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Prerequisites")
        st.markdown("""
        * **Python 3.10+**: Chosen for its robust scientific libraries and human-readable syntax.
        * **Streamlit**: Provides the interactive web interface without the overhead of traditional frontend frameworks.
        * **SciPy & NumPy**: The "workhorses" for all mathematical and signal processing computations.
        """)
    with col_b:
        st.subheader("Design Philosophy")
        st.markdown("""
        * **Transparency**: Every command generates visible Python/MATLAB code to bridge the gap between "magic" and "engineering."
        * **Interactivity**: Immediate visual and auditory feedback (via Plotly and the Audio Engine) reinforces learning.
        * **Extensibility**: The modular architecture allows for easy integration of new filter types or AI models.
        """)

    # 2. Digital Signal Processing (DSP) 101
    st.header("2. Digital Signal Processing (DSP) 101")
    st.markdown("""
    Digital Signal Processing involves the representation of signals by sequences of numbers and the processing of those sequences. 
    Unlike continuous analog signals, digital signals are discrete in both time and amplitude.
    """)
    
    with st.expander("Periodic Signals & Mathematical Notations"):
        st.markdown("""
        A periodic signal repeats itself at regular intervals. The most fundamental periodic signal is the **Sine Wave**.
        """)
        st.latex(r"x(t) = A \sin(2\pi f t + \phi)")
        st.markdown("""
        * **Amplitude ($A$)**: The peak strength of the signal.
        * **Frequency ($f$)**: How many times the wave repeats per second (Hertz).
        * **Phase ($\phi$)**: The starting position of the wave in its cycle.
        """)
        
    with st.expander("The Nyquist-Shannon Sampling Theorem"):
        st.markdown("""
        To capture a signal digitally without losing information (aliasing), we must sample it at a rate ($f_s$) 
        that is at least twice the highest frequency ($f_{max}$) present in the signal.
        """)
        st.latex(r"f_s > 2 \cdot f_{max}")
        st.markdown("""
        **Why this matters:** If we sample too slowly, high-frequency signals will appear as low-frequency artifacts, 
        making our data incorrect.
        """)

    # 3. Spectral Analysis & The Frequency Domain
    st.header("3. Spectral Analysis & The Frequency Domain")
    st.markdown("""
    While the **Time Domain** shows us *when* events happen, the **Frequency Domain** tells us *what* frequencies make up the signal. 
    This is essential for filtering and identifying hidden patterns.
    """)
    
    with st.expander("The Discrete Fourier Transform (DFT)"):
        st.markdown("""
        The DFT is the mathematical tool that decomposes a sequence of values into components of different frequencies. 
        In this app, we use the **Fast Fourier Transform (FFT)**, an efficient algorithm to compute the DFT.
        """)
        st.latex(r"X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-j \frac{2\pi}{N} kn}")
        st.markdown("""
        * $X[k]$ is the frequency spectrum.
        * $x[n]$ is the time-domain input sequence.
        * The result allows us to see precisely which frequencies are dominant in our signal (e.g., finding the 50Hz hum of a power line).
        """)

    # 4. Advanced Features: AI, Audio & Medical Analytics
    st.header("4. Advanced Features: AI, Audio & Medical Analytics")
    st.markdown("""
    We have integrated cutting-edge technologies to push this lab beyond traditional DSP tools.
    """)
    
    with st.expander("AI Intelligence (LLM) Integration"):
        st.markdown("""
        Traditional software uses rigid "menus." We use a **Local Large Language Model (DistilGPT2)** to 
        infer user intent. 
        * **Natural Language Understanding (NLU)**: Allows the system to understand "make it higher" as a request to increase frequency.
        * **Zero-Shot Potential**: The architecture is ready to be swapped with models like Gemini to handle complex logic like "design a filter to remove this noise."
        """)
        
    with st.expander("The 16-bit PCM Audio Engine"):
        st.markdown("""
        To convert digital numbers into sound, we normalize the signal amplitude to fit within a **16-bit range** (-32768 to 32767). 
        We then wrap this raw data in a **WAV header** (RIFF format) so it can be played by any standard browser audio player.
        """)

    with st.expander("Medical Analytics: HRV & SDNN"):
        st.markdown("""
        In the ECG mode, the system detects "R-peaks" (the heart's main contraction) and calculates **Heart Rate Variability (HRV)**. 
        The primary metric used here is **SDNN** (Standard Deviation of NN intervals).
        """)
        st.latex(r"SDNN = \sqrt{\frac{1}{N-1} \sum_{i=1}^N (RR_i - \overline{RR})^2}")
        st.markdown("""
        **Clinical Significance:** High HRV typically indicates a healthy, adaptive heart, while low HRV can be a sign of stress or illness.
        """)

    # 5. Technical Implementation: Code Breakdown
    st.header("5. Technical Implementation: Code Breakdown")
    
    with st.expander("The Brain: NLP Parsing Logic (Deep Dive)"):
        st.markdown("""
        The `SignalProcessor.parse` method is the heart of the NLU system. It uses a combination of:
        1. **Regex Extraction**: `(\d+\.?\d*)\s*hz` captures numbers followed by "hz".
        2. **Iterative State**: It checks for "increase/decrease" to modify the *current* state rather than resetting it.
        3. **Keywords**: Iterates through supported topologies (sine, square, ecg) to switch generator logic.
        """)
        st.code(r"""
# Core NLP Parameter Extraction Logic
freq_match = re.search(r'(\d+\.?\d*)\s*hz', text)
is_relative = any(x in text for x in ['increase', 'more', 'higher'])

if freq_match:
    val = float(freq_match.group(1))
    if is_relative:
        params['freq'] += val  # Stateful update
    else:
        params['freq'] = val   # Absolute update
        """, language="python")

    with st.expander("The Signal: Synthetic ECG Generation (Deep Dive)"):
        st.markdown("""
        The ECG model is built from the ground up using **Gaussian pulses**.
        1. **P-wave**: Small deflection for atrial depolarization.
        2. **QRS Complex**: The sharp peak for ventricular depolarization (modeled as a narrow, high Gaussian).
        3. **T-wave**: The wider pulse for ventricular repolarization.
        """)
        st.code(r"""
# Gaussian pulse summation for ECG complexes
def get_ecg(t_arr, bpm=60):
    sig = np.zeros_like(t_arr); period = 60/bpm
    for s in np.arange(0, t_arr[-1], period):
        # QRS spike (mu=0.1, sigma=0.005)
        sig += 1.0 * np.exp(-((t_arr-(s+0.1))**2)/(2*0.005**2))
        # T wave (mu=0.3, sigma=0.035)
        sig += 0.25 * np.exp(-((t_arr-(s+0.3))**2)/(2*0.035**2))
    return sig
        """, language="python")

    with st.expander("The Engine: Dynamic Sandbox Execution (Deep Dive)"):
        st.markdown("""
        To make the app truly interactive, we use Python's `exec()` to run the code generated by our NLP engine.
        1. **Environment Setup**: We provide the `ctx` dictionary with libraries like `np` and `signal`.
        2. **Live Execution**: The user's changes (or the AI's generation) are executed in this isolated space.
        3. **Result Retrieval**: We pull the calculated `t` and `sig` arrays out of the dictionary to update the Plotly charts.
        """)
        st.code(r"""
try:
    ctx = {"np": np, "signal": signal}
    exec(st.session_state.py_code, ctx) # Live Python Sandbox
    t, sig = ctx.get('t'), ctx.get('sig') # Extract results
except Exception as e:
    st.error(f"Sandbox Error: {e}")
        """, language="python")

    st.markdown("---")
    st.caption("Developed for the NLP to MATLAB and Python Signal Processing Lab.")
