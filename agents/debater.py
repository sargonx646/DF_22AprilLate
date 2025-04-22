import json
import os
import time
import signal
from openai import OpenAI
from typing import List, Dict
from config import DEBATE_ROUNDS, MAX_TOKENS, TIMEOUT_S

class TimeoutException(Exception):
    """Custom exception for global simulation timeout."""
    pass

def timeout_handler(signum, frame):
    """Handler for global timeout signal."""
    raise TimeoutException("Simulation exceeded maximum allowed time.")

def simulate_debate(personas: List[Dict], dilemma: str, process_hint: str, extracted: Dict, scenarios: str = "", rounds: int = DEBATE_ROUNDS, max_simulation_time: int = 120) -> List[Dict]:
    """
    Simulate a human-like, constructive debate among stakeholder personas using xAI's Grok-3-Beta. Each stakeholder is prompted individually
    with tailored instructions based on their role, expertise, and the current round's objectives, ensuring domain-specific and meaningful contributions.
    The simulation dynamically follows the extracted decision-making process, adapting prompts to each round and integrating responses into a transcript.
    A global timeout ensures the simulation does not exceed the specified maximum time.

    Args:
        personas (List[Dict]): List of personas with name, goals, biases, tone, bio, and expected behavior.
        dilemma (str): The user-provided decision dilemma.
        process_hint (str): The user-provided process and stakeholder details.
        extracted (Dict): Extracted decision structure with process steps and stakeholder roles.
        scenarios (str): Optional alternative scenarios or external factors.
        rounds (int): Number of debate rounds, aligned with process steps.
        max_simulation_time (int): Maximum allowed time for the entire simulation in seconds (default: 120).

    Returns:
        List[Dict]: Debate transcript with agent, round, step, and message.
    """
    # Set up global timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(max_simulation_time)

    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    transcript = []
    process_steps = extracted.get("process", [])
    if len(process_steps) < rounds:
        process_steps.extend([process_steps[-1]] * (rounds - len(process_steps)))
    process_steps = process_steps[:rounds]

    # Map stakeholders to roles for domain-specific prompting
    stakeholder_roles = {}
    for line in process_hint.split("\n"):
        if ":" in line and any(s["name"] in line for s in extracted.get("stakeholders", [])):
            name, role = line.split(":", 1)
            name = name.strip().split(".")[-1].strip()
            role = role.strip()
            # Exclude USAID-related roles
            if "USAID" not in role:
                stakeholder_roles[name] = role

    # Filter personas to exclude USAID-related stakeholders
    filtered_personas = [persona for persona in personas if "USAID" not in stakeholder_roles.get(persona["name"], "")]

    # Define role-specific focus areas for prompting
    role_focus = {
        "Manager": "Focus on overall strategy, team coordination, and resource allocation.",
        "Expert": "Focus on technical feasibility, innovation, and expertise in your domain.",
        "Team Lead": "Focus on team dynamics, implementation challenges, and collaboration.",
        "Analyst": "Focus on data-driven insights, risk assessment, and cost-benefit analysis.",
        "Financial Officer": "Focus on budget implications, financial risks, and cost efficiency.",
        "Environmental Advocate": "Focus on sustainability, environmental impact, and long-term ecological benefits.",
        "Community Representative": "Focus on community needs, social impact, and stakeholder engagement.",
        "Marketing Director": "Focus on brand impact, market trends, and customer perception.",
        "Program Manager": "Focus on project feasibility, timelines, and operational challenges.",
        "Field Coordinator": "Focus on on-the-ground realities, urgent needs, and practical implementation.",
        "Donor Representative": "Focus on alignment with donor priorities, funding constraints, and ROI for donors.",
        "Assistant Secretary for the Bureau of East Asian and Pacific Affairs": "Focus on regional stability, diplomatic strategy, and resource allocation across humanitarian, security, and economic priorities.",
        "Director, Bureau for Humanitarian Assistance - BHA": "Focus on humanitarian crisis response, relief logistics, and immediate life-saving interventions.",
        "DoD Liaison": "Focus on national security interests, military readiness, and strategic stability.",
        "Assistant Secretary for the Bureau of Economic and Business Affairs": "Focus on economic growth, infrastructure investments, and long-term regional resilience."
    }

    # Define process-step-specific objectives for each round
    process_objectives = {
        "Situation Assessment": "Analyze the dilemma and gather relevant data from your perspective. Identify key challenges, risks, and priorities based on your expertise. Provide specific insights or data points that should be considered.",
        "Options Development": "Propose 2–3 actionable options to address the dilemma, emphasizing priorities relevant to your role. Evaluate the pros and cons of each option, considering the data and stakeholder dynamics from previous rounds.",
        "Interagency Coordination": "Coordinate with other stakeholders to refine options into a cohesive plan. Address conflicts, propose compromises, and ensure alignment across priorities.",
        "Task Force Deliberation": "Deliberate on the proposed plan, focusing on implementation details, anticipating challenges, and suggesting mitigation strategies.",
        "Recommendation and Approval": "Finalize the recommendation, justify your stance, and propose next steps for approval and implementation."
    }

    # Initialize cumulative context
    cumulative_context = "Initial Context: The debate begins with the following dilemma and process.\n"
    cumulative_context += f"Dilemma: {dilemma}\nProcess: {process_hint}\n"
    if scenarios:
        cumulative_context += f"Alternative Scenarios/External Factors: {scenarios}\n"

    try:
        # Simulate debate round by round
        for round_num in range(rounds):
            current_step = process_steps[round_num]
            # Extract the step name for matching with objectives
            step_key = current_step.split("(")[0].strip()
            objective = process_objectives.get(step_key, "Continue the discussion, building on prior rounds to finalize the decision from your perspective.")

            round_transcript = []
            # Prompt each stakeholder individually
            for persona in filtered_personas:
                stakeholder_name = persona["name"]
                role = stakeholder_roles.get(stakeholder_name, "Team Member")
                focus_area = role_focus.get(role, "Focus on general contributions to the decision-making process.")

                # Simplified prompt to avoid token limits
                prompt = (
                    f"You are Grok-3-Beta, simulating {stakeholder_name}, with the role of {role}. "
                    f"Your expertise and focus area: {focus_area}\n"
                    "Your characteristics:\n"
                    f"- Goals: {', '.join(persona['goals'])}\n"
                    f"- Biases: {', '.join(persona['biases'])}\n"
                    f"- Tone: {persona['tone']}\n"
                    f"- Bio: {persona['bio'][:200]}\n"
                    f"- Expected Behavior: {persona['expected_behavior'][:100]}\n"
                    f"Current Step: {current_step} (Round {round_num + 1})\n"
                    f"Objective: {objective}\n"
                    "Instructions:\n"
                    "- Provide a 200–300 word response, focusing on the dilemma and current step, from your role’s perspective.\n"
                    "- Use Chain-of-Thought reasoning: Consider your goals, biases, tone, and expected behavior.\n"
                    "- Propose actionable solutions, anticipate challenges, and suggest innovations.\n"
                    "- Reference the cumulative context, e.g., 'As [Stakeholder X] noted...'\n"
                    "- Engage constructively, proposing compromises and resolving conflicts.\n"
                    f"Cumulative Context (summarized):\n{cumulative_context[-1000:]}\n"
                    "Return your response as a JSON object with keys 'agent', 'round', 'step', and 'message'."
                )

                try:
                    completion = client.chat.completions.create(
                        model="grok-3-beta",
                        messages=[
                            {"role": "system", "content": "You are an AI assistant simulating a stakeholder in a debate."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=800,
                        timeout=10
                    )
                    raw_response = completion.choices[0].message.content
                    response = json.loads(raw_response)
                    if isinstance(response, dict) and all(key in response for key in ["agent", "round", "step", "message"]):
                        round_transcript.append(response)
                    else:
                        raise ValueError("Invalid JSON structure")
                except Exception as e:
                    print(f"Error for {stakeholder_name} (Round {round_num + 1}): {str(e)}")
                    raise  # Let the exception propagate to fail fast since fallback is not needed

            # Add round contributions to transcript and update cumulative context
            transcript.extend(round_transcript)
            cumulative_context += f"\nRound {round_num + 1} ({current_step}) Contributions:\n"
            for entry in round_transcript:
                cumulative_context += f"- {entry['agent']}: {entry['message']}\n"

    except TimeoutException:
        print(f"Simulation interrupted: Exceeded maximum time of {max_simulation_time} seconds.")
        # Add a note to the transcript
        if transcript:
            transcript.append({
                "agent": "System",
                "round": round_num + 1 if 'round_num' in locals() else 1,
                "step": current_step if 'current_step' in locals() else "Unknown",
                "message": f"Simulation interrupted: Exceeded maximum time of {max_simulation_time} seconds. Results up to this point are provided."
            })
    finally:
        signal.alarm(0)  # Disable the alarm

    return transcript
