import streamlit as st
import json
import time
import random
from streamlit.components.v1 import html
from agents.extractor import extract_info
from agents.persona_builder import build_personas
from agents.debater import simulate_debate
from agents.summarizer import summarize_and_analyze
from utils.visualizer import generate_visuals
from utils.db import init_db, save_simulation, get_all_personas

# Initialize database
init_db()

# Streamlit configuration
st.set_page_config(page_title="Twin Decision Making AI Companion", page_icon="🤖", layout="wide")
st.markdown('<link rel="stylesheet" href="/static/css/custom.css">', unsafe_allow_html=True)
st.markdown('<script src="/static/js/animations.js"></script>', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">', unsafe_allow_html=True)

# Sample prompts for auto-fill
SAMPLE_PROMPTS = [
    {
        "dilemma": """
You are the senior leadership team at the U.S. State Department, tasked with allocating a $500 million emergency aid package to stabilize a volatile region in the Indo-Pacific, where rising tensions threaten U.S. strategic interests. The region faces three simultaneous challenges:
1. Humanitarian Crisis in Country A: A devastating typhoon has displaced 500,000 people, requiring immediate relief (food, medical supplies, temporary shelters) to prevent a humanitarian catastrophe and maintain U.S. soft power influence.
2. Security Threats in Country B: Escalating insurgent activities near critical maritime trade routes demand rapid military and police training programs to bolster local forces, ensuring freedom of navigation and countering rival powers’ influence.
3. Economic Instability in Country C: A collapsing economy risks destabilizing a key U.S. ally, necessitating investments in infrastructure (ports, energy) to restore growth and prevent alignment with adversarial blocs.
You have $500 million to allocate across three initiatives:
- Humanitarian Relief for Country A: $300 million to fund emergency aid (UNICEF, NGOs) and reconstruction, delivering 80% coverage of displaced populations but yielding limited long-term strategic gains.
- Security Assistance for Country B: $250 million for training, equipment, and intelligence-sharing with local forces, securing trade routes but risking domestic backlash over military spending.
- Economic Investment for Country C: $200 million for port modernization and energy projects, fostering long-term stability but with a 12–18 month payoff horizon and high corruption risks.
How should you allocate the $500 million to balance:
- Humanitarian Impact: Saving lives and enhancing U.S. moral credibility.
- Strategic Security: Protecting maritime routes and countering rival influence.
- Economic Stability: Strengthening allies and preventing geopolitical shifts.
- Political Viability: Managing Congressional oversight and public opinion.
""",
        "process_hint": """
The allocation decision follows a structured State Department process, overseen by a cross-functional task force over a 4-week period:
1. Situation Assessment (Week 1):
   - Bureau of East Asian and Pacific Affairs (EAP) compiles a regional threat analysis, detailing humanitarian needs, security risks, and economic vulnerabilities.
   - Office of Foreign Assistance (F) estimates aid absorption capacity for each country.
2. Options Development (Week 1–2):
   - Bureau of Political-Military Affairs (PM) drafts a security assistance plan for Country B, including cost-benefit analysis of military training.
   - Bureau of Economic and Business Affairs (EB) proposes infrastructure investments for Country C, with risk assessments for corruption.
   - Bureau for Humanitarian Assistance (BHA) outlines relief logistics for Country A, prioritizing speed and coverage.
3. Interagency Coordination (Week 2–3):
   - USAID provides technical expertise on aid delivery and local partnerships.
   - Department of Defense (DoD) evaluates strategic implications of security investments, including naval base access.
   - Office of Management and Budget (OMB) reviews fiscal constraints and Congressional funding conditions.
4. Task Force Deliberation (Week 3):
   - A 2-day offsite with key stakeholders to debate trade-offs, using:
     - A decision matrix scoring each initiative on humanitarian impact, security gains, economic ROI, and political feasibility.
     - Scenario planning for worst-case outcomes (e.g., aid mismanagement, insurgent escalation, economic collapse).
5. Recommendation and Approval (Week 4):
   - Task force submits a prioritized allocation plan to the Secretary of State.
   - Deputy Secretary for Management and Resources ensures compliance with Congressional appropriations.
   - Final approval by the Secretary, followed by briefings to the National Security Council (NSC) and Congressional committees.
Key Stakeholders:
1. Elizabeth Carter, Assistant Secretary, EAP: Advocates for balanced regional strategy, prioritizing U.S. influence.
2. Michael Nguyen, Director, BHA: Pushes for maximum humanitarian aid to Country A to save lives.
3. General Laura Thompson, DoD Liaison: Emphasizes security assistance for Country B to protect trade routes.
4. Dr. Priya Sharma, Assistant Secretary, EB: Champions economic investments in Country C for long-term stability.
5. James Sullivan, USAID Coordinator: Focuses on aid effectiveness and local capacity.
6. Rebecca Ortiz, OMB Analyst: Ensures fiscal discipline and Congressional alignment.
7. Senator Robert Kline, Senate Foreign Relations Committee: Influences funding through oversight, wary of military spending.
Stakeholder Dynamics:
- Carter seeks a holistic approach but faces pressure from Thompson (security) and Nguyen (humanitarian).
- Sharma and Sullivan clash over short-term aid vs. long-term investments.
- Ortiz and Kline constrain the budget, demanding measurable outcomes.
- All stakeholders report to the Secretary of State, who balances diplomacy, security, and politics.
"""
    },
    # Other prompts omitted for brevity but remain unchanged
]

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
    st.session_state.prompt_index = 0

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

# Onboarding modal (no button, static display)
if not st.session_state.get("onboarding_seen", False):
    st.markdown('''
    <div class="modal">
        <div class="modal-content">
            <h2>Welcome to Your Twin Decision Making AI Companion!</h2>
            <p>Recreate and test your decision-making processes with AI:</p>
            <ul>
                <li>Define your decision context and process.</li>
                <li>Review and edit AI-extracted stakeholders.</li>
                <li>Explore dynamic personas.</li>
                <li>Simulate stakeholder debates.</li>
                <li>Unlock insights and optimizations.</li>
            </ul>
        </div>
    </div>
    <script>
        setTimeout(() => {
            document.querySelector('.modal').style.display = 'none';
        }, 5000); // Auto-hide after 5 seconds
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
            value=st.session_state.dilemma,
            placeholder="E.g., Allocate $500M for regional stabilization, balancing humanitarian aid, security, and economic growth.",
            height=200,
            help="Describe the decision you face, including goals and constraints (e.g., budget, time, priorities)."
        )
        st.markdown('<h4><i class="fas fa-users"></i> Process or Stakeholders</h4>', unsafe_allow_html=True)
        process_hint = st.text_area(
            "",
            value=st.session_state.process_hint,
            placeholder="E.g., Involves a task force with Assistant Secretary, USAID, DoD, and OMB, following a 4-week process.",
            height=200,
            help="Detail the decision-making process (steps, timeline) and/or key stakeholders (names, roles, priorities)."
        )
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Extract Decision Structure")
        with col2:
            if st.form_submit_button("Generate Sample Prompt"):
                st.session_state.prompt_index = (st.session_state.prompt_index + 1) % len(SAMPLE_PROMPTS)
                st.session_state.dilemma = SAMPLE_PROMPTS[st.session_state.prompt_index]["dilemma"]
                st.session_state.process_hint = SAMPLE_PROMPTS[st.session_state.prompt_index]["process_hint"]
                st.rerun()
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

# Step 2: Review and Edit Decision Structure
elif st.session_state.step == 2:
    st.header("Step 2: Review and Edit Decision Structure")
    st.info("Review the AI-extracted decision type, stakeholders, issues, and process steps. Edit as needed before generating personas.")
    if st.session_state.extracted:
        with st.form("edit_extraction_form"):
            st.markdown("### Decision Type")
            decision_type = st.selectbox(
                "Decision Type",
                options=DECISION_TYPES,
                index=DECISION_TYPES.index(st.session_state.extracted.get("decision_type", "Other"))
            )
            st.markdown("### Stakeholders")
            stakeholders = []
            for i, s in enumerate(st.session_state.extracted.get("stakeholders", [])):
                st.markdown(f"#### Stakeholder {i+1}")
                name = st.text_input(f"Name {i+1}", value=s.get("name", ""), key=f"stakeholder_name_{i}")
                traits = st.selectbox(
                    f"Psychological Traits {i+1}",
                    options=STAKEHOLDER_ANALYSIS['psychological_traits'],
                    index=STAKEHOLDER_ANALYSIS['psychological_traits'].index(s.get("psychological_traits", STAKEHOLDER_ANALYSIS['psychological_traits'][0])),
                    key=f"stakeholder_traits_{i}"
                )
                influences = st.selectbox(
                    f"Influences {i+1}",
                    options=STAKEHOLDER_ANALYSIS['influences'],
                    index=STAKEHOLDER_ANALYSIS['influences'].index(s.get("influences", STAKEHOLDER_ANALYSIS['influences'][0])),
                    key=f"stakeholder_influences_{i}"
                )
                biases = st.selectbox(
                    f"Biases {i+1}",
                    options=STAKEHOLDER_ANALYSIS['biases'],
                    index=STAKEHOLDER_ANALYSIS['biases'].index(s.get("biases", STAKEHOLDER_ANALYSIS['biases'][0])),
                    key=f"stakeholder_biases_{i}"
                )
                history = st.selectbox(
                    f"Historical Behavior {i+1}",
                    options=STAKEHOLDER_ANALYSIS['historical_behavior'],
                    index=STAKEHOLDER_ANALYSIS['historical_behavior'].index(s.get("historical_behavior", STAKEHOLDER_ANALYSIS['historical_behavior'][0])),
                    key=f"stakeholder_history_{i}"
                )
                stakeholders.append({
                    "name": name,
                    "psychological_traits": traits,
                    "influences": influences,
                    "biases": biases,
                    "historical_behavior": history
                })
            st.markdown("### Issues")
            issues = st.text_area(
                "Issues (one per line)",
                value="\n".join(st.session_state.extracted.get("issues", [])),
                height=100
            )
            st.markdown("### Process Steps")
            process = st.text_area(
                "Process Steps (one per line)",
                value="\n".join(st.session_state.extracted.get("process", [])),
                height=100
            )
            st.markdown("### ASCII Process Timeline")
            st.code(st.session_state.extracted.get("ascii_process", "No process visualization available."))
            st.markdown("### ASCII Stakeholder Hierarchy")
            st.code(st.session_state.extracted.get("ascii_stakeholders", "No stakeholder visualization available."))
            if st.form_submit_button("Save and Generate Personas"):
                try:
                    edited_extracted = {
                        "decision_type": decision_type,
                        "stakeholders": stakeholders,
                        "issues": [i.strip() for i in issues.split("\n") if i.strip()],
                        "process": [p.strip() for p in process.split("\n") if p.strip()],
                        "ascii_process": generate_ascii_process([p.strip() for p in process.split("\n") if p.strip()]),
                        "ascii_stakeholders": generate_ascii_stakeholders(stakeholders)
                    }
                    if not (MIN_STAKEHOLDERS <= len(edited_extracted["stakeholders"]) <= MAX_STAKEHOLDERS):
                        st.error(f"The simulation requires {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} stakeholders.")
                    else:
                        st.session_state.extracted = edited_extracted
                        with st.spinner("Crafting stakeholder personas..."):
                            st.session_state.personas = build_personas([s["name"] for s in edited_extracted["stakeholders"]])
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
    st.info("Discover and manage AI-crafted personas, or search previously saved personas.")
    
    st.markdown("### Search Saved Personas")
    saved_personas = get_all_personas()
    persona_names = [p["name"] for p in saved_personas]
    search_query = st.text_input("Search for a persona by name:", "")
    filtered_personas = [p for p in saved_personas if search_query.lower() in p["name"].lower()]
    
    if filtered_personas:
        st.markdown("#### Matching Personas")
        selected_persona = st.selectbox("Select a persona to view or edit:", [p["name"] for p in filtered_personas])
        persona_data = next(p for p in filtered_personas if p["name"] == selected_persona)
        with st.form(f"edit_persona_{selected_persona}"):
            st.markdown("#### Edit Persona")
            name = st.text_input("Name", value=persona_data["name"])
            goals = st.text_area("Goals", value=", ".join(persona_data["goals"]))
            biases = st.text_area("Biases", value=", ".join(persona_data["biases"]))
            tone = st.text_input("Tone", value=persona_data["tone"])
            if st.form_submit_button("Save Changes"):
                updated_persona = {
                    "name": name,
                    "goals": goals.split(", "),
                    "biases": biases.split(", "),
                    "tone": tone
                }
                st.session_state.personas = [updated_persona if p["name"] == selected_persona else p for p in st.session_state.personas]
                st.success(f"Persona {name} updated!")
    
    st.markdown("### Current Personas")
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
        time.sleep(0.5)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("Analyze and Optimize", key="analyze"):
        try:
            with st.spinner("Analyzing debate and generating insights..."):
                st.session_state.summary, st.session_state.keywords, st.session_state.suggestion = summarize_and_analyze(st.session_state.transcript)
                generate_visuals(st.session_state.keywords, st.session_state.transcript)
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
