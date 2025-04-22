import streamlit as st
import json
import time
import random
from streamlit.components.v1 import html
from agents.extractor import extract_info, generate_ascii_process, generate_ascii_stakeholders
from agents.persona_builder import build_personas
from agents.debater import simulate_debate
from agents.summarizer import summarize_and_analyze
from utils.visualizer import generate_visuals
from utils.db import init_db, save_simulation, get_all_personas
from config import DECISION_TYPES, STAKEHOLDER_ANALYSIS, MIN_STAKEHOLDERS, MAX_STAKEHOLDERS
from openai import OpenAI
import os

# Initialize database
init_db()

# Streamlit configuration
st.set_page_config(page_title="DecisionTwin for Decision Making", page_icon="🤖", layout="wide")
st.markdown('<link rel="stylesheet" href="/static/css/custom.css">', unsafe_allow_html=True)
st.markdown('<script src="/static/js/animations.js"></script>', unsafe_allow_html=True)
st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">', unsafe_allow_html=True)

# Display the DecisionForge logo above the title
st.image("https://raw.githubusercontent.com/your-username/df_22aprillate/main/assets/decisionforge_logo.png", width=300)

# Custom header with title and description
st.markdown('''
<div class="header-container">
    <h1 class="header-title">DecisionTwin for Decision Making</h1>
    <p class="header-subtitle">Recreate and Test Your Decision-Making Processes with AI-Powered Simulations</p>
</div>
''', unsafe_allow_html=True)

# Initialize session state
if "step" not in st.session_state:
    st.session_state.step = 1
    st.session_state.dilemma = ""
    st.session_state.process_hint = ""
    st.session_state.scenarios = ""
    st.session_state.extracted = None
    st.session_state.personas = []
    st.session_state.transcript = []
    st.session_state.summary = ""
    st.session_state.keywords = []
    st.session_state.suggestion = ""

# Sidebar with progress and navigation
st.sidebar.image("https://raw.githubusercontent.com/your-username/df_22aprillate/main/assets/geometric_shape.png", width=100)
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
            <h2>Welcome to DecisionTwin for Decision Making!</h2>
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

# Function to generate a sample prompt dynamically using AI
def generate_sample_prompt():
    """
    Generate a dynamic decision-making scenario using xAI's Grok-3-Beta.

    Returns:
        Dict: A dictionary with 'dilemma', 'process_hint', and 'scenarios'.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    prompt = (
        "You are an AI assistant for DecisionTwin for Decision Making, a tool designed to simulate decision-making processes for senior leaders. "
        "Generate a realistic decision-making scenario for a high-stakes situation that requires balancing multiple priorities. The scenario should be unique and diverse, avoiding repetition of common themes like disaster relief or corporate R&D budgets unless significantly varied. Include:\n"
        "1. **Dilemma (300–400 words)**: Describe a complex decision context faced by a leadership team (e.g., government agency, NGO, corporation, or city council). Include 3–4 competing priorities (e.g., public safety, economic growth, environmental impact, political pressure), specific initiatives with costs, and goals to balance (e.g., stakeholder satisfaction, long-term stability, immediate impact).\n"
        "2. **Process Hint (200–300 words)**: Outline a structured decision-making process (4–6 steps, with timeline), key stakeholders (6–8 individuals with names, roles, and priorities), and stakeholder dynamics (e.g., conflicts, alliances).\n"
        "3. **Alternative Scenarios (50–100 words)**: Provide 2–3 external factors or scenarios that could impact the decision (e.g., budget cuts, public backlash, technological failures).\n"
        "Return the results in JSON format with fields 'dilemma', 'process_hint', and 'scenarios'."
    )

    try:
        completion = client.chat.completions.create(
            model="grok-3-beta",
            messages=[
                {"role": "system", "content": "You are an AI assistant generating decision-making scenarios."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        result = json.loads(completion.choices[0].message.content)
        return {
            "dilemma": result.get("dilemma", ""),
            "process_hint": result.get("process_hint", ""),
            "scenarios": result.get("scenarios", "")
        }
    except Exception as e:
        print(f"Sample Prompt Generation Error: {str(e)}")
        return {
            "dilemma": "A leadership team must decide how to allocate resources in a high-stakes situation. Details could not be generated due to an error.",
            "process_hint": "The process involves multiple stakeholders and steps. Please define manually.",
            "scenarios": "Consider potential external factors that may arise."
        }

# Step 1: Craft Your Decision-Making Process
if st.session_state.step == 1:
    st.header("Step 1: Craft Your Decision-Making Process")
    st.markdown('''
    <div class="step-info">
        <i class="fas fa-brain step-icon"></i>
        <p>Describe your decision context and the stakeholders or process involved. DecisionTwin for Decision Making will simulate and test your process, providing actionable insights.</p>
    </div>
    ''', unsafe_allow_html=True)
    with st.form("input_form"):
        st.markdown('<h4><i class="fas fa-lightbulb"></i> Decision Context</h4>', unsafe_allow_html=True)
        dilemma = st.text_area(
            "",
            value=st.session_state.dilemma,
            placeholder="E.g., Allocate resources for a high-stakes project, balancing multiple priorities.",
            height=200,
            help="Describe the decision you face, including goals and constraints (e.g., budget, time, priorities)."
        )
        st.markdown('<h4><i class="fas fa-users"></i> Process or Stakeholders</h4>', unsafe_allow_html=True)
        process_hint = st.text_area(
            "",
            value=st.session_state.process_hint,
            placeholder="E.g., Involves a task force with multiple stakeholders, following a structured process.",
            height=200,
            help="Detail the decision-making process (steps, timeline) and/or key stakeholders (names, roles, priorities)."
        )
        st.markdown('<h4><i class="fas fa-exclamation-circle"></i> Alternative Scenarios or External Factors (Optional)</h4>', unsafe_allow_html=True)
        scenarios = st.text_area(
            "",
            value=st.session_state.scenarios,
            placeholder="E.g., Budget cuts, delays in implementation, unexpected external pressures.",
            height=150,
            help="Provide alternative scenarios or external factors to test different outcomes (optional)."
        )
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Extract Decision Structure")
        with col2:
            if st.form_submit_button("Generate Sample Prompt"):
                with st.spinner("Generating a sample decision-making scenario..."):
                    sample_prompt = generate_sample_prompt()
                    st.session_state.dilemma = sample_prompt["dilemma"]
                    st.session_state.process_hint = sample_prompt["process_hint"]
                    st.session_state.scenarios = sample_prompt["scenarios"]
                st.rerun()
        if submitted:
            if not dilemma.strip() or not process_hint.strip():
                st.error("Please provide both a decision context and process/stakeholder details.")
            else:
                try:
                    with st.spinner("Analyzing your decision process..."):
                        st.session_state.dilemma = dilemma
                        st.session_state.process_hint = process_hint
                        st.session_state.scenarios = scenarios
                        st.session_state.extracted = extract_info(dilemma, process_hint, scenarios)
                    st.session_state.step = 2
                    st.success("Decision structure extracted successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to extract structure: {str(e)}. Please check your input or try again.")

# Step 2: Review and Edit Decision Structure
elif st.session_state.step == 2:
    st.header("Step 2: Review and Edit Decision Structure")
    st.info("Review the AI-extracted decision type, stakeholders, issues, process steps, and external factors. Edit as needed before generating personas.")
    if st.session_state.extracted:
        with st.form("edit_extraction_form"):
            # Decision Type Section
            st.markdown("### Decision Type")
            extracted_decision_type = st.session_state.extracted.get("decision_type", "Other")
            # Handle cases where decision_type includes annotations like "(Assumed)"
            base_decision_type = extracted_decision_type.split(" (")[0].strip()
            # Ensure the base_decision_type exists in DECISION_TYPES, default to "Other" if not
            if base_decision_type not in DECISION_TYPES:
                base_decision_type = "Other"
            decision_type = st.selectbox(
                "Decision Type",
                options=DECISION_TYPES,
                index=DECISION_TYPES.index(base_decision_type),
                help="The type of decision being made, as extracted by AI."
            )

            # Stakeholders Section with Editable Cards
            st.markdown("### Stakeholders (Editable Cards)")
            st.markdown("""
            <style>
            .stakeholder-card {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 15px;
            }
            .stakeholder-card input, .stakeholder-card textarea {
                width: 100%;
                margin-bottom: 10px;
            }
            </style>
            """, unsafe_allow_html=True)
            cols = st.columns(4)  # 4 cards per row
            stakeholders = []
            for i, s in enumerate(st.session_state.extracted.get("stakeholders", [])):
                with cols[i % 4]:
                    st.markdown(f'<div class="stakeholder-card">', unsafe_allow_html=True)
                    name = st.text_input(f"Name", value=s.get("name", ""), key=f"stakeholder_name_{i}")
                    role = st.text_input(f"Role", value=s.get("role", ""), key=f"stakeholder_role_{i}")
                    traits = st.text_area(
                        f"Psychological Traits (Suggestions: {', '.join(STAKEHOLDER_ANALYSIS['psychological_traits'])})",
                        value=s.get("psychological_traits", ""),
                        key=f"stakeholder_traits_{i}",
                        height=50
                    )
                    influences = st.text_area(
                        f"Influences (Suggestions: {', '.join(STAKEHOLDER_ANALYSIS['influences'])})",
                        value=s.get("influences", ""),
                        key=f"stakeholder_influences_{i}",
                        height=50
                    )
                    biases = st.text_area(
                        f"Biases (Suggestions: {', '.join(STAKEHOLDER_ANALYSIS['biases'])})",
                        value=s.get("biases", ""),
                        key=f"stakeholder_biases_{i}",
                        height=50
                    )
                    history = st.text_area(
                        f"Historical Behavior (Suggestions: {', '.join(STAKEHOLDER_ANALYSIS['historical_behavior'])})",
                        value=s.get("historical_behavior", ""),
                        key=f"stakeholder_history_{i}",
                        height=50
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
                    stakeholders.append({
                        "name": name,
                        "role": role,
                        "psychological_traits": traits,
                        "influences": influences,
                        "biases": biases,
                        "historical_behavior": history
                    })

            # Issues Section
            st.markdown("### Issues")
            issues = st.text_area(
                "Issues (one per line)",
                value="\n".join(st.session_state.extracted.get("issues", [])),
                height=100
            )

            # Process Steps Section
            st.markdown("### Process Steps")
            process = st.text_area(
                "Process Steps (one per line)",
                value="\n".join(st.session_state.extracted.get("process", [])),
                height=100
            )

            # External Factors Section
            st.markdown("### External Factors")
            external_factors = st.text_area(
                "External Factors (one per line)",
                value="\n".join(st.session_state.extracted.get("external_factors", [])),
                height=100
            )

            # ASCII Visualizations
            st.markdown("### ASCII Process Timeline")
            st.code(st.session_state.extracted.get("ascii_process", "No process visualization available."))
            st.markdown("### ASCII Stakeholder Hierarchy")
            st.code(st.session_state.extracted.get("ascii_stakeholders", "No stakeholder visualization available."))

            # Submit Button
            submit_button = st.form_submit_button("Save and Generate Personas")

            if submit_button:
                try:
                    edited_extracted = {
                        "decision_type": decision_type,
                        "stakeholders": stakeholders,
                        "issues": [i.strip() for i in issues.split("\n") if i.strip()],
                        "process": [p.strip() for p in process.split("\n") if p.strip()],
                        "external_factors": [e.strip() for e in external_factors.split("\n") if e.strip()],
                        "ascii_process": generate_ascii_process([p.strip() for p in process.split("\n") if p.strip()]),
                        "ascii_stakeholders": generate_ascii_stakeholders(stakeholders)
                    }
                    if not (MIN_STAKEHOLDERS <= len(edited_extracted["stakeholders"]) <= MAX_STAKEHOLDERS):
                        st.error(f"The simulation requires {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} stakeholders.")
                    else:
                        st.session_state.extracted = edited_extracted
                        with st.spinner("Crafting stakeholder personas..."):
                            st.session_state.personas = build_personas(
                                [s["name"] for s in edited_extracted["stakeholders"]],
                                st.session_state.dilemma,
                                st.session_state.process_hint
                            )
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
    st.info("Review and modify the AI-crafted personas, or search previously saved personas.")
    
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
            bio = st.text_area("Bio", value=persona_data["bio"], height=150)
            expected_behavior = st.text_area("Expected Behavior", value=persona_data["expected_behavior"], height=100)
            if st.form_submit_button("Save Changes"):
                updated_persona = {
                    "name": name,
                    "goals": goals.split(", "),
                    "biases": biases.split(", "),
                    "tone": tone,
                    "bio": bio,
                    "expected_behavior": expected_behavior
                }
                st.session_state.personas = [updated_persona if p["name"] == selected_persona else p for p in st.session_state.personas]
                st.success(f"Persona {name} updated!")
    
    st.markdown("### Current Personas")
    stakeholder_titles = {}
    for line in st.session_state.process_hint.split("\n"):
        if ":" in line and any(s["name"] in line for s in st.session_state.extracted.get("stakeholders", [])):
            name, title = line.split(":", 1)
            name = name.strip().split(".")[-1].strip()
            title = title.strip()
            stakeholder_titles[name] = title
    
    cols = st.columns(3)
    for i, persona in enumerate(st.session_state.personas):
        with cols[i % 3]:
            title = stakeholder_titles.get(persona["name"], "Unknown Role")
            emoji = "🌐" if "EAP" in title else "🩺" if "BHA" in title else "🛡️" if "DoD" in title else "💼" if "EB" in title else "🤝" if "USAID" in title else "📊" if "OMB" in title else "🏛️" if "Senate" in title else "👤"
            st.markdown(f'''
            <div class="persona-card">
                <h3>{persona['name']}</h3>
                <p><strong>Title:</strong> {title} {emoji}</p>
                <p><strong>Goals:</strong> {', '.join(persona['goals'])}</p>
                <p><strong>Biases:</strong> {', '.join(persona['biases'])}</p>
                <p><strong>Tone:</strong> {persona['tone'].capitalize()}</p>
                <p><strong>Bio:</strong> {persona['bio']}</p>
                <p><strong>Expected Behavior:</strong> {persona['expected_behavior']}</p>
            </div>
            ''', unsafe_allow_html=True)
    if st.button("Launch Simulation", key="launch_simulation"):
        try:
            with st.spinner("Initiating simulation..."):
                st.session_state.transcript = simulate_debate(
                    personas=st.session_state.personas,
                    dilemma=st.session_state.dilemma,
                    process_hint=st.session_state.process_hint,
                    extracted=st.session_state.extracted,
                    scenarios=st.session_state.scenarios
                )
            st.session_state.step = 4
            st.success("Simulation complete! Watch the debate unfold.")
            st.rerun()
        except Exception as e:
            st.error(f"Simulation failed: {str(e)}")

# Step 4: View Simulation
elif st.session_state.step == 4:
    st.header("Step 4: Experience the Debate")
    st.info("Witness your stakeholders debate in real-time, following the decision-making process. Ready to analyze the results?")
    
    # Custom CSS for debate visualization
    st.markdown('''
    <style>
    .debate-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        position: relative;
        min-height: 400px;
        overflow: hidden;
    }
    .debate-window {
        position: relative;
        width: 100%;
        height: 400px;
        overflow-y: auto;
        margin-top: 20px;
        padding: 10px;
        background-color: #fff;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    .speech-bubble {
        background-color: rgba(255, 255, 255, 0.9);
        border: 2px solid #007bff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        font-size: 14px;
        animation: fadeInOut 5s ease-in-out;
        z-index: 10;
        opacity: 0.8;
        line-height: 1.5;
    }
    @keyframes fadeInOut {
        0% { opacity: 0; transform: translateY(20px); }
        10% { opacity: 0.8; transform: translateY(0); }
        90% { opacity: 0.8; transform: translateY(0); }
        100% { opacity: 0; transform: translateY(-20px); }
    }
    </style>
    ''', unsafe_allow_html=True)

    # Debate visualization
    st.markdown('<div class="debate-container">', unsafe_allow_html=True)
    
    # Display debate with round and step information
    st.markdown('<div class="debate-window">', unsafe_allow_html=True)
    debate_placeholder = st.empty()
    current_round = None
    for entry in st.session_state.transcript:
        agent = entry["agent"]
        message = entry["message"]
        round_num = entry["round"]
        step = entry["step"]
        
        # Display round and step header
        if current_round != round_num:
            debate_placeholder.markdown(f"### Round {round_num}: {step}")
            current_round = round_num
        
        # Generate HTML for the speech bubble
        html_content = f'<div class="speech-bubble"><strong>{agent}:</strong><br>{message}</div>'
        
        with debate_placeholder.container():
            st.markdown(html_content, unsafe_allow_html=True)
        time.sleep(1.0)  # Slower pacing for longer responses
    
    st.markdown('</div>', unsafe_allow_html=True)
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
            with open("network_graph.html", "r") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=400)
            st.caption("Stakeholder Interaction Network")
        except FileNotFoundError:
            st.warning("Network graph unavailable.")
    
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
            with open("network_graph.html", "r") as f:
                st.download_button(
                    label="📊 Network Graph (HTML)",
                    data=f,
                    file_name="network_graph.html",
                    mime="text/html"
                )
        except FileNotFoundError:
            st.warning("Network graph unavailable.")
    
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
