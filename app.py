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
    {
        "dilemma": """
You are the executive board of TechNova, a global technology firm, deciding how to invest a $100 million R&D budget to maintain competitive edge in the AI market. The industry faces rapid innovation cycles, and you must address three priorities:
1. Advanced AI Model Development: Build a proprietary large language model to rival industry leaders, requiring significant computational resources.
2. Edge AI Solutions: Develop lightweight AI for IoT devices, targeting smart homes and industrial applications, with growing market demand.
3. Ethical AI Framework: Invest in responsible AI practices to comply with emerging regulations and build consumer trust.
You have $100 million to allocate across three initiatives:
- AI Model Development: $60 million for compute infrastructure and talent, promising high market share but with long development timelines.
- Edge AI Solutions: $30 million for hardware partnerships and prototyping, offering quick market entry but lower margins.
- Ethical AI Framework: $20 million for compliance tools and transparency audits, enhancing brand reputation but with indirect financial returns.
How should you allocate the $100 million to balance:
- Innovation Leadership: Staying ahead of competitors in AI capabilities.
- Market Growth: Capturing emerging opportunities in IoT and consumer markets.
- Regulatory Compliance: Mitigating risks and building trust.
- Financial Returns: Ensuring investor confidence and profitability.
""",
        "process_hint": """
The decision follows a 6-week strategic planning process, managed by a cross-functional R&D committee:
1. Market Analysis (Week 1):
   - Chief Technology Officer (CTO) assesses competitor AI models and market trends.
   - Marketing Director evaluates consumer demand for edge AI and ethical concerns.
2. Proposal Drafting (Week 2–3):
   - Head of AI Research proposes a detailed plan for the large language model, including resource needs.
   - IoT Division Lead outlines edge AI development timelines and partnerships.
   - Chief Ethics Officer drafts a framework for responsible AI, aligning with EU regulations.
3. Financial Review (Week 3–4):
   - CFO conducts ROI and risk analysis for each initiative.
   - Investor Relations Manager gathers feedback from top shareholders.
4. Committee Workshop (Week 5):
   - A 2-day session to prioritize initiatives, using:
     - A weighted scoring model for innovation, market potential, compliance, and ROI.
     - Scenario analysis for risks (e.g., regulatory fines, market delays).
5. Board Approval (Week 6):
   - Committee submits recommendations to the CEO and Board.
   - Board votes on the allocation, with final sign-off by the CEO.
Key Stakeholders:
1. Dr. Elena Martinez, CEO: Drives long-term vision, balancing innovation and profitability.
2. Raj Patel, CTO: Advocates for cutting-edge AI model development.
3. Sarah Kim, IoT Division Lead: Pushes for edge AI to capture market share.
4. Prof. Alan Becker, Chief Ethics Officer: Prioritizes ethical AI to avoid regulatory risks.
5. Linda Wong, CFO: Focuses on financial viability and investor expectations.
6. Michael Chen, Marketing Director: Emphasizes consumer trust and market positioning.
7. Emily Harper, Investor Relations Manager: Represents shareholder interests, wary of high-risk investments.
8. Dr. Sofia Alvarez, Head of AI Research: Supports advanced AI development for technical leadership.
Stakeholder Dynamics:
- Martinez mediates between Patel’s innovation focus and Wong’s financial caution.
- Kim and Becker clash over short-term market gains vs. long-term ethical investments.
- Harper and Chen align on brand reputation but differ on investment scale.
- All report to Martinez, who ensures strategic alignment.
"""
    },
    {
        "dilemma": """
You are the city council of Greenview, a mid-sized coastal city, tasked with allocating a $50 million community development fund to address climate resilience and urban growth. The city faces three pressing challenges:
1. Coastal Flooding: Rising sea levels threaten residential areas, requiring immediate infrastructure upgrades.
2. Affordable Housing Shortage: Population growth demands new housing units to prevent displacement of low-income residents.
3. Green Energy Transition: Public pressure calls for renewable energy projects to reduce carbon emissions.
You have $50 million to allocate across three initiatives:
- Flood Defense Systems: $30 million for seawalls and drainage, protecting 70% of at-risk areas but with high maintenance costs.
- Affordable Housing Projects: $25 million for 1,000 new units, addressing housing needs but facing zoning disputes.
- Solar Energy Program: $15 million for community solar farms, cutting emissions but with a 5-year ROI.
How should you allocate the $50 million to balance:
- Community Safety: Protecting residents from flooding risks.
- Social Equity: Ensuring housing access for all income levels.
- Environmental Sustainability: Meeting climate goals and public expectations.
- Political Support: Gaining voter and business approval.
""",
        "process_hint": """
The allocation decision follows a 3-month public consultation process, overseen by a council task force:
1. Community Needs Assessment (Month 1):
   - Environmental Planner compiles flood risk data and climate projections.
   - Housing Authority assesses housing demand and zoning constraints.
2. Proposal Development (Month 1–2):
   - Public Works Director drafts flood defense plans, including cost estimates.
   - Community Development Director proposes housing projects with local partnerships.
   - Sustainability Coordinator outlines solar energy plans, leveraging state grants.
3. Public Engagement (Month 2):
   - Town hall meetings gather resident feedback on priorities.
   - Business Association provides input on economic impacts.
4. Council Deliberation (Month 3):
   - A 1-day session to evaluate proposals, using:
     - A community impact scorecard for safety, equity, sustainability, and feasibility.
     - Risk assessment for project delays or budget overruns.
5. Final Vote (End of Month 3):
   - Council votes on the allocation, with the Mayor breaking ties.
   - Approved plan is submitted for state funding review.
Key Stakeholders:
1. Mayor Lisa Thompson: Seeks balanced solutions to maintain voter support.
2. Dr. Maria Gonzalez, Environmental Planner: Prioritizes flood defenses for safety.
3. James Lee, Housing Authority Director: Advocates for affordable housing to address equity.
4. Rachel Patel, Sustainability Coordinator: Pushes for solar energy to meet climate goals.
5. Tom Harris, Public Works Director: Focuses on infrastructure feasibility and costs.
6. Susan Carter, Community Development Director: Supports housing to prevent displacement.
7. David Nguyen, Business Association President: Emphasizes economic benefits and business support.
8. Emily Rivera, Resident Advocate: Represents community concerns, wary of tax increases.
Stakeholder Dynamics:
- Thompson balances Gonzalez’s safety focus with Lee’s equity concerns.
- Patel and Harris clash over green energy vs. immediate infrastructure needs.
- Nguyen and Rivera debate business interests vs. resident priorities.
- All report to the council, with Thompson leading consensus-building.
"""
    }
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

# Step 2: Review Extracted Structure
elif st.session_state.step == 2:
    st.header("Step 2: Review Decision Structure")
    st.info("Examine the AI-identified decision type, stakeholders, issues, and process steps, including ASCII visualizations.")
    if st.session_state.extracted:
        st.markdown("### Decision Type")
        st.write(st.session_state.extracted.get("decision_type", "N/A"))
        st.markdown("### Stakeholders")
        st.json(st.session_state.extracted.get("stakeholders", []))
        st.markdown("### Issues")
        st.write(st.session_state.extracted.get("issues", []))
        st.markdown("### Process Steps")
        st.write(st.session_state.extracted.get("process", []))
        st.markdown("### ASCII Process Timeline")
        st.code(st.session_state.extracted.get("ascii_process", "No process visualization available."))
        st.markdown("### ASCII Stakeholder Hierarchy")
        st.code(st.session_state.extracted.get("ascii_stakeholders", "No stakeholder visualization available."))
        if st.button("Generate Personas", key="generate_personas"):
            try:
                stakeholders = st.session_state.extracted.get("stakeholders", [])
                if not stakeholders or len(stakeholders) < 3 or len(stakeholders) > 10:
                    st.error("The simulation requires 3–10 stakeholders.")
                else:
                    with st.spinner("Crafting stakeholder personas..."):
                        st.session_state.personas = build_personas([s["name"] for s in stakeholders])
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
    
    # Persona Search and Navigation
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
