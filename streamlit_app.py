import streamlit as st
import time
import os
import pandas as pd
import altair as alt
import librosa
import numpy as np
from audio_stream import AudioRecorder

# Ensuring we use the robust final logic
try:
    from final_detector import VoiceFirewall
except ImportError:
    from detector_v3 import VoiceFirewall

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="AspitaTech Defense",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS THEME ---
st.markdown("""
<style>
    /* Global Styles */
    .stApp { background-color: #F8F9FA; color: #0F172A; }

    /* Navigation Buttons */
    div.stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 700;
        border: 1px solid #E2E8F0;
        padding: 15px 10px;
        font-size: 16px;
        background-color: white;
        color: #334155;
        transition: all 0.2s;
    }
    div.stButton > button:hover {
        border-color: #3B82F6;
        color: #3B82F6;
        transform: translateY(-2px);
    }

    /* Cards */
    .css-card {
        background-color: #FFFFFF;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #E2E8F0;
        margin-bottom: 20px;
    }

    /* Guides */
    .step-guide {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        color: #1E3A8A;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 25px;
        font-size: 15px;
    }

    /* Alerts */
    .alert-box { padding: 20px; border-radius: 10px; margin-bottom: 15px; }
    .alert-red { background-color: #FEF2F2; border-left: 8px solid #EF4444; color: #991B1B; }
    .alert-green { background-color: #ECFDF5; border-left: 8px solid #10B981; color: #065F46; }
</style>
""", unsafe_allow_html=True)

# --- INITIALIZE STATE ---
if 'recorder' not in st.session_state: st.session_state.recorder = AudioRecorder()
if 'firewall' not in st.session_state: st.session_state.firewall = VoiceFirewall()
if 'history' not in st.session_state: st.session_state.history = []
if 'is_running' not in st.session_state: st.session_state.is_running = False
if 'current_mode' not in st.session_state: st.session_state.current_mode = "Home"

# --- TOP NAVIGATION BAR ---
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 1])

with col_nav1:
    if st.button("🏠 Home"):
        st.session_state.current_mode = "Home"
        st.rerun()
with col_nav2:
    if st.button("🧪 Simulation (Try First)"):  # Promoted
        st.session_state.current_mode = "Sim"
        st.rerun()
with col_nav3:
    if st.button("📡 Live Defense"):
        st.session_state.current_mode = "Live"
        st.rerun()
with col_nav4:
    if st.button("📂 File Audit"):
        st.session_state.current_mode = "File"
        st.rerun()

st.divider()

# --- MODE 1: HOME ---
if st.session_state.current_mode == "Home":
    st.markdown("# 🛡️ AspitaTech Voice Security")
    st.markdown("### Select a Mode:")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="css-card">
            <h3>🧪 Simulation Lab</h3>
            <p><strong>Step 1: Start Here.</strong></p>
            <p>Test the system with pre-loaded 'Real' vs 'Fake' audio to see the detection graph in action.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Simulation", key="home_sim"):
            st.session_state.current_mode = "Sim"
            st.rerun()

    with c2:
        st.markdown("""
        <div class="css-card">
            <h3>📡 Live Defense</h3>
            <p><strong>Step 2: Real Usage.</strong></p>
            <p>Monitor your actual computer audio (Zoom/YouTube) in real-time for deepfakes.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to Live Defense", key="home_live"):
            st.session_state.current_mode = "Live"
            st.rerun()

    with c3:
        st.markdown("""
        <div class="css-card">
            <h3>📂 File Audit</h3>
            <p><strong>Step 3: Forensics.</strong></p>
            <p>Upload suspicious files (.WAV) to get an instant biometric verification report.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Go to File Audit", key="home_file"):
            st.session_state.current_mode = "File"
            st.rerun()

# --- MODE 2: SIMULATION (GLITCH FIXED) ---
elif st.session_state.current_mode == "Sim":
    st.markdown("# 🧪 Simulation Lab")

    st.markdown("""
    <div class="step-guide">
        <h4>⚡ HOW TO DEMO:</h4>
        1️⃣ <strong>Auto-Start:</strong> The system is running in the background.<br>
        2️⃣ <strong>Play Audio:</strong> Click the buttons below.<br>
        3️⃣ <strong>Watch Result:</strong> The graph will appear at the <strong>bottom</strong>.
    </div>
    """, unsafe_allow_html=True)

    # Auto-start engine if needed
    if not st.session_state.is_running:
        st.session_state.recorder.start()
        st.session_state.is_running = True
        time.sleep(0.5)

    # 1. Controls (Buttons First)
    st.markdown("### 🎛️ Test Controls")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("#### 🗣️ Real Human Voice")
        st.audio("assets/real_test.wav", format="audio/wav")
        st.success("✅ EXPECTED: GREEN Graph")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.markdown("#### 🤖 AI Deepfake")
        st.audio("assets/fake_test.wav", format="audio/wav")
        st.error("⚠️ EXPECTED: RED Graph")
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. Visualization (Bottom & Stable)
    st.divider()
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### 📊 Live Resonance Graph")
        # Placeholders allow updating WITHOUT reloading the page
        chart_placeholder = st.empty()
        alert_placeholder = st.empty()

    # 3. Logic Loop (NO RERUN)
    placeholder_file = "live_stream_buffer.wav"

    if st.session_state.is_running:
        # We loop here without st.rerun() to prevent glitches
        while st.session_state.current_mode == "Sim":
            success = st.session_state.recorder.save_current_buffer(placeholder_file)
            if success:
                label, score = st.session_state.firewall.analyze(placeholder_file)
                timestamp = time.strftime("%H:%M:%S")

                # Logic
                risk_score = score * 100 if label == "FAKE" else (1.0 - score) * 5
                st.session_state.history.append({"Time": timestamp, "Risk Score": risk_score})
                if len(st.session_state.history) > 40: st.session_state.history.pop(0)

                # Update Alerts (Smooth)
                if label == "FAKE":
                    alert_placeholder.markdown(
                        f"""<div class="alert-box alert-red"><h3>⚠️ DEEPFAKE DETECTED</h3>Confidence: {score * 100:.1f}%</div>""",
                        unsafe_allow_html=True)
                elif label == "REAL":
                    alert_placeholder.markdown(
                        f"""<div class="alert-box alert-green"><h3>🛡️ VERIFIED HUMAN</h3>Confidence: {score * 100:.1f}%</div>""",
                        unsafe_allow_html=True)

                # Update Chart (Smooth)
                df = pd.DataFrame(st.session_state.history)
                if not df.empty:
                    chart = alt.Chart(df).mark_area(
                        line={'color': '#6366f1'},
                        color=alt.Gradient(
                            gradient='linear',
                            stops=[alt.GradientStop(color='rgba(99, 102, 241, 0.5)', offset=0),
                                   alt.GradientStop(color='rgba(99, 102, 241, 0.05)', offset=1)],
                            x1=1, x2=1, y1=1, y2=0
                        )
                    ).encode(
                        x=alt.X('Time', axis=None),
                        y=alt.Y('Risk Score', scale=alt.Scale(domain=[0, 100]))
                    ).properties(height=250)
                    chart_placeholder.altair_chart(chart, use_container_width=True)

            # Wait a bit to prevent CPU spike
            time.sleep(0.5)

# --- MODE 3: LIVE DEFENSE ---
elif st.session_state.current_mode == "Live":
    st.markdown("# 📡 Live Call Monitor")

    st.markdown("""
    <div class="step-guide">
        <h4>⚡ QUICK GUIDE: LIVE MODE</h4>
        1️⃣ <strong>Start:</strong> Click 'START PROTECTION' below.<br>
        2️⃣ <strong>Use:</strong> Go to your Zoom call or YouTube video.<br>
        3️⃣ <strong>Monitor:</strong> This screen will flag any deepfakes instantly.
    </div>
    """, unsafe_allow_html=True)

    # Controls
    m1, m2 = st.columns([1, 2])
    with m1:
        st.markdown('<div class="css-card">', unsafe_allow_html=True)
        st.metric("System Status", "ACTIVE" if st.session_state.is_running else "PAUSED")
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        if st.session_state.is_running:
            if st.button("⏹ STOP PROTECTION", type="primary", use_container_width=True):
                st.session_state.recorder.stop()
                st.session_state.is_running = False
                st.rerun()
        else:
            if st.button("▶ START PROTECTION", type="primary", use_container_width=True):
                st.session_state.recorder.start()
                st.session_state.is_running = True
                st.session_state.history = []
                st.rerun()

    # Visualization
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Real-Time Resonance")
        chart_placeholder = st.empty()
        alert_placeholder = st.empty()
    with c2:
        st.markdown("### Audit Log")
        log_container = st.container(height=300)

    if st.session_state.is_running:
        placeholder_file = "live_stream_buffer.wav"
        # LOOP FIX: No st.rerun() here either
        while st.session_state.current_mode == "Live" and st.session_state.is_running:
            success = st.session_state.recorder.save_current_buffer(placeholder_file)
            if success:
                label, score = st.session_state.firewall.analyze(placeholder_file)
                timestamp = time.strftime("%H:%M:%S")
                risk_score = score * 100 if label == "FAKE" else (1.0 - score) * 5
                st.session_state.history.append({"Time": timestamp, "Risk Score": risk_score})
                if len(st.session_state.history) > 40: st.session_state.history.pop(0)

                if label == "FAKE":
                    alert_placeholder.markdown(
                        f"""<div class="alert-box alert-red"><h3>⚠️ DEEPFAKE DETECTED</h3>Confidence: {score * 100:.1f}%</div>""",
                        unsafe_allow_html=True)
                elif label == "REAL":
                    alert_placeholder.markdown(
                        f"""<div class="alert-box alert-green"><h3>🛡️ VERIFIED HUMAN</h3>Confidence: {score * 100:.1f}%</div>""",
                        unsafe_allow_html=True)

                df = pd.DataFrame(st.session_state.history)
                if not df.empty:
                    chart = alt.Chart(df).mark_area(
                        line={'color': '#6366f1'},
                        color=alt.Gradient(
                            gradient='linear',
                            stops=[alt.GradientStop(color='rgba(99, 102, 241, 0.5)', offset=0),
                                   alt.GradientStop(color='rgba(99, 102, 241, 0.05)', offset=1)],
                            x1=1, x2=1, y1=1, y2=0
                        )
                    ).encode(
                        x=alt.X('Time', axis=None),
                        y=alt.Y('Risk Score', scale=alt.Scale(domain=[0, 100]))
                    ).properties(height=250)
                    chart_placeholder.altair_chart(chart, use_container_width=True)

                with log_container:
                    icon = "🔴" if label == "FAKE" else "🟢"
                    st.markdown(f"**{timestamp}** | {icon} {label} ({score:.2f})")
            time.sleep(0.5)

# --- MODE 4: FILE AUDIT ---
elif st.session_state.current_mode == "File":
    st.markdown("# 📂 Forensic File Audit")

    st.markdown("""
    <div class="step-guide">
        <h4>⚡ QUICK GUIDE: FORENSICS</h4>
        1️⃣ <strong>Upload:</strong> Drag & Drop a .WAV file below.<br>
        2️⃣ <strong>Scan:</strong> Click 'Analyze File'.<br>
        3️⃣ <strong>Result:</strong> Get a trusted Biometric Verification Report.
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Audio Evidence", type=["wav"])

    if uploaded_file is not None:
        if st.button("🔍 Analyze File", type="primary"):
            with st.spinner("Processing Forensics..."):
                temp_filename = "temp_upload.wav"
                with open(temp_filename, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                try:
                    label, score = st.session_state.firewall.analyze(temp_filename)
                    st.divider()

                    if label == "FAKE":
                        st.markdown(f"""
                        <div class="alert-box alert-red">
                            <h2>⚠️ EVIDENCE TAMPERED (FAKE)</h2>
                            <p><strong>Confidence:</strong> {score * 100:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="alert-box alert-green">
                            <h2>✅ EVIDENCE VERIFIED (REAL)</h2>
                            <p><strong>Confidence:</strong> {score * 100:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)

                    if os.path.exists(temp_filename): os.remove(temp_filename)

                except Exception as e:
                    st.error(f"Analysis Error: {e}")