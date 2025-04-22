import streamlit as st
import json
import time
from streamlit.components.v1 import html
from agents.extractor import extract_info
from agents.persona_builder import build_personas
from agents.debater import simulate_debate
from agents.summarizer import summarize_and_analyze
from utils.visualizer import generate_visuals
from utils.db import init_db, save_simulation

# Initialize database
init_db()

# Streamlit configuration
st.set_page_config(page_title="Twin Decision Making AI Companion", page_icon="🤖", layout="wide")
st.markdown('<link rel="stylesheet" href="/static/css/custom.css">', unsafe_allow_html=True)
st.markdown('<script src="/static/js/animations.js"></script>', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">', unsafe_allow_html=True)

# Custom header with animation
st.markdown('''
<div class="header-container">
    <h1 class="header-title">Twin Decision Making AI Companion</h1>
    <p class="header-subtitle">Recreate and Test Your Decision-Making Processes with AI-Powered Simulations</p>
</div>
''', unsafe_allow_html=True)

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.dilemma = ""
    st.session_state.process_hint = ""
    st.session_state.extracted = None
    st.session_state.personas = []
    st.session_state.transcript = []
    st.session_state.summary = ""
    st.session_state.keywords = []
    st.session_state.suggestion = ""

# Sidebar with progress and navigation
st.sidebar.title("Decision-Making Journey")
st.sidebar.markdown("Track your simulation progress:")
progress = st.sidebar.progress(st.session_state.step / 5)
st.sidebar.markdown(f"**Step {st.session_state.step} of 5**")
if st.session_state.step > 1:
    if st.sidebar.button("🔙 Back to Input", key="back_to_1"):
        st.session_state.step = 1
        st.rerun()
if st.session_state.step > 2:
    if st.sidebar.button("🔙 Back to Personas", key="back_to_2"):
        st.session_state.step = 2
        st.rerun()
if st.session_state.step > 3:
    if st.sidebar.button("🔙 Back to Simulation", key="back_to_3"):
        st.session_state.step = 3
        st.rerun()
if st.session_state.step > 4:
    if st.sidebar.button("🔙 Back to Results", key="back_to_4"):
        st.session_state.step = 4
        st.rerun()

# Onboarding modal (shown on first load)
if not st.session_state.get("onboarding_seen", False):
    st.markdown('''
    <div class="modal">
        <div class="modal-content">
            <h2>Welcome to Your Twin Decision Making AI Companion!</h2>
            <p>Recreate and test your decision-making processes with AI:</p>
            <ul>
                <li>Define your decision context and process.</li>
                <li>Review AI-extracted stakeholders.</li>
                <li>Explore dynamic personas.</li>
                <li>Simulate stakeholder debates.</li>
                <li>Unlock insights and optimizations.</li>
            </ul>
            <button onclick="closeModal()">Start Now</button>
        </div>
    </div>
    <script>
        function closeModal() {
            document.querySelector('.modal').style.display = 'none';
        }
    </script>
    ''', unsafe_allow_html=True)
    st.session_state.onboarding_seen = True

# Step 1: Craft Your Decision-Making Process
if st.session_state.step == 1:
    st.header("Step 1: Craft Your Decision-Making Process")
    st.markdown('''
    <div class="step-info">
        <i class="fas fa-brain step-icon"></i>
        <p>Describe your decision context and the stakeholders or process involved. Your Twin AI Companion will simulate and test your process, providing actionable insights.</p>
    </div>
    ''', unsafe_allow_html=True)
    with st.form("input_form"):
        st.markdown('<h4><i class="fas fa-lightbulb"></i> Decision Context</h4>', unsafe_allow_html=True)
        dilemma = st.text_area(
            "",
            placeholder="E.g., Allocate $500M for regional stabilization, balancing humanitarian aid, security, and economic growth.",
            height=200,
            help="Describe the decision you face, including goals and constraints (e.g., budget, time, priorities)."
        )
        st.markdown('<h4><i class="fas fa-users"></i> Process or Stakeholders</h4>', unsafe_allow_html=True)
        process_hint = st.text_area(
            "",
            placeholder="E.g., Involves a task force with Assistant Secretary, USAID, DoD, and OMB, following a 4-week process.",
            height=200,
            help="Detail the decision-making process (steps, timeline) and/or key stakeholders (names, roles, priorities)."
        )
        submitted = st.form_submit_button("Extract Decision Structure")
        if submitted:
            if not dilemma.strip() or not process_hint.strip():
                st.error("Please provide both a decision context and process/stakeholder details.")
            else:
                try:
                    with st.spinner("Analyzing your decision process..."):
                        st.session_state.dilemma = dilemma
                        st.session_state.process_hint = process_hint
                        st.session_state.extracted = extract_info(dilemma, process_hint)
                    st.session_state.step = 2
                    st.success("Decision structure extracted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to extract structure: {str(e)}. Please check your input or try again.")

# Step 2: Review Extracted Structure
elif st.session_state.step == 2:
    st.header("Step 2: Review Decision Structure")
    st.info("Examine the AI-identified stakeholders, issues, and process steps. Ready to create personas?")
    if st.session_state.extracted:
        st.json(st.session_state.extracted)
        if st.button("Generate Personas", key="generate_personas"):
            try:
                stakeholders = st.session_state.extracted.get("stakeholders", [])
                if not stakeholders or len(stakeholders) < 3 or len(stakeholders) > 8:
                    st.error("The simulation requires 3–8 stakeholders.")
                else:
                    with st.spinner("Crafting stakeholder personas..."):
                        st.session_state.personas = build_personas(stakeholders)
                    st.session_state.step = 3
                    st.success("Personas generated successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"Persona generation failed: {str(e)}")
    else:
        st.error("No structure extracted. Please return to Step 1.")

# Step 3: Review Personas
elif st.session_state.step == 3:
    st.header("Step 3: Meet Your Stakeholders")
    st.info("Discover the AI-crafted personas, each with unique goals, biases, and tones. Ready to see them debate?")
    cols = st.columns(3)
    for i, persona in enumerate(st.session_state.personas):
        with cols[i % 3]:
            st.markdown(f'''
            <div class="persona-card">
                <h3>{persona['name']}</h3>
                <p><strong>Goals:</strong> {', '.join(persona['goals'])}</p>
                <p><strong>Biases:</strong> {', '.join(persona['biases'])}</p>
                <p><strong>Tone:</strong> {persona['tone'].capitalize()}</p>
            </div>
            ''', unsafe_allow_html=True)
    if st.button("Launch Simulation", key="launch_simulation"):
        try:
            with st.spinner("Initiating simulation..."):
                st.session_state.transcript = simulate_debate(st.session_state.personas)
            st.session_state.step = 4
            st.success("Simulation complete! Watch the debate unfold.")
            st.rerun()
        except Exception as e:
            st.error(f"Simulation failed: {str(e)}")

# Step 4: View Simulation
elif st.session_state.step == 4:
    st.header("Step 4: Experience the Debate")
    st.info("Witness your stakeholders debate in real-time. Ready to analyze the results?")
    st.markdown('<div class="debate-container">', unsafe_allow_html=True)
    placeholder = st.empty()
    for entry in st.session_state.transcript:
        with placeholder.container():
            st.markdown(
                f'<div class="debate-message"><strong>{entry["agent"]}:</strong> {entry["message"]}</div>',
                unsafe_allow_html=True
            )
        time.sleep(0.5)  # Simulate live typing for immersive effect
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Analyze and Optimize", key="analyze"):
        try:
            with st.spinner("Analyzing debate and generating insights..."):
                st.session_state.summary, st.session_state.keywords, st.session_state.suggestion = summarize_and_analyze(st.session_state.transcript)
                generate_visuals(st.session_state.keywords, st.session_state.transcript)
                # Save to database
                save_simulation(
                    st.session_state.dilemma,
                    st.session_state.process_hint,
                    st.session_state.extracted,
                    st.session_state.personas,
                    st.session_state.transcript,
                    st.session_state.summary,
                    st.session_state.keywords,
                    st.session_state.suggestion
                )
            st.session_state.step = 5
            st.success("Analysis complete! Explore your insights.")
            st.rerun()
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

# Step 5: View Results
elif st.session_state.step == 5:
    st.header("Step 5: Unlock Your Insights")
    st.info("Dive into the simulation results, optimization suggestions, and stunning visualizations.")
    st.markdown("### Decision Summary")
    st.markdown(f'<div class="summary-box">{st.session_state.summary}</div>', unsafe_allow_html=True)
    
    st.markdown("### Optimization Suggestion")
    st.markdown(f'<div class="suggestion-box">{st.session_state.suggestion}</div>', unsafe_allow_html=True)
    
    st.markdown("### Visual Insights")
    col1, col2 = st.columns(2)
    with col1:
        try:
            st.image("visualization.png", caption="Word Cloud of Key Themes", use_column_width=True)
        except FileNotFoundError:
            st.warning("Word cloud unavailable.")
    with col2:
        try:
            st.image("heatmap.png", caption="Stakeholder Activity Heatmap", use_column_width=True)
        except FileNotFoundError:
            st.warning("Heatmap unavailable.")
    
    st.markdown("### Export Your Results")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.download_button(
            label="📄 Transcript (JSON)",
            data=json.dumps(st.session_state.transcript, indent=2),
            file_name="transcript.json",
            mime="application/json"
        )
    with col2:
        st.download_button(
            label="📝 Summary (TXT)",
            data=st.session_state.summary,
            file_name="summary.txt",
            mime="text/plain"
        )
    with col3:
        try:
            with open("visualization.png", "rb") as f:
                st.download_button(
                    label="🖼️ Word Cloud (PNG)",
                    data=f,
                    file_name="visualization.png",
                    mime="image/png"
                )
        except FileNotFoundError:
            st.warning("Word cloud unavailable.")
    with col4:
        try:
            with open("heatmap.png", "rb") as f:
                st.download_button(
                    label="📊 Heatmap (PNG)",
                    data=f,
                    file_name="heatmap.png",
                    mime="image/png"
                )
        except FileNotFoundError:
            st.warning("Heatmap unavailable.")
    
    # Call to action
    st.markdown('''
    <div class="cta-box">
        <h3>Loved the Experience?</h3>
        <p>Share your feedback or start a new simulation to explore more possibilities!</p>
        <button onclick="restartSimulation()">Start New Simulation</button>
    </div>
    <script>
        function restartSimulation() {
            window.location.reload();
        }
    </script>
    ''', unsafe_allow_html=True)
