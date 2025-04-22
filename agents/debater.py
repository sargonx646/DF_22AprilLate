import json
import os
import time
from openai import OpenAI
from typing import List, Dict
from config import DEBATE_ROUNDS, MAX_TOKENS, TIMEOUT_S

def simulate_debate(personas: List[Dict], dilemma: str, process_hint: str, extracted: Dict, scenarios: str = "", rounds: int = DEBATE_ROUNDS) -> List[Dict]:
    """
    Simulate a human-like, constructive debate among stakeholder personas using xAI's Grok-3-Beta. Each stakeholder is prompted individually
    with tailored instructions based on their role, expertise, and the current round's objectives, ensuring domain-specific and meaningful contributions.
    The simulation dynamically follows the extracted decision-making process, adapting prompts to each round and integrating responses into a transcript.

    Args:
        personas (List[Dict]): List of personas with name, goals, biases, tone, bio, and expected behavior.
        dilemma (str): The user-provided decision dilemma.
        process_hint (str): The user-provided process and stakeholder details.
        extracted (Dict): Extracted decision structure with process steps and stakeholder roles.
        scenarios (str): Optional alternative scenarios or external factors.
        rounds (int): Number of debate rounds, aligned with process steps.

    Returns:
        List[Dict]: Debate transcript with agent, round, step, and message.
    """
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
            stakeholder_roles[name] = role

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
        "Donor Representative": "Focus on alignment with donor priorities, funding constraints, and ROI for donors."
    }

    # Define process-step-specific objectives for each round
    process_objectives = {
        "Data Collection": "Analyze the dilemma and gather relevant data from your perspective. Identify key challenges, risks, and priorities based on your expertise. Provide specific insights or data points that should be considered.",
        "Stakeholder Mapping": "Identify the priorities and influence of key stakeholders, including yourself, from your perspective. Highlight potential allies, conflicts, or power dynamics that could impact the decision-making process.",
        "Option Development": "Propose 2–3 actionable options to address the dilemma, emphasizing priorities relevant to your role. Evaluate the pros and cons of each option, considering the data and stakeholder dynamics from previous rounds.",
        "Impact Analysis": "Evaluate the short- and long-term outcomes of the proposed options from your perspective. Use simulations or reasoning to assess impacts on relevant metrics (e.g., GDP, safety, satisfaction) and identify potential risks or benefits.",
        "Stakeholder Consultation": "Negotiate trade-offs and propose compromises to align on a final recommendation. Address conflicts from previous rounds, engage with other stakeholders’ proposals, and suggest ways to build consensus."
    }

    # Initialize cumulative context
    cumulative_context = "Initial Context: The debate begins with the following dilemma and process.\n"
    cumulative_context += f"Dilemma: {dilemma}\nProcess: {process_hint}\n"
    if scenarios:
        cumulative_context += f"Alternative Scenarios/External Factors: {scenarios}\n"

    # Simulate debate round by round
    for round_num in range(rounds):
        current_step = process_steps[round_num]
        # Extract the step name for matching with objectives (e.g., "Data Collection" from "Data Collection (Week 1): ...")
        step_key = current_step.split("(")[0].strip()
        objective = process_objectives.get(step_key, "Continue the discussion, building on prior rounds to finalize the decision from your perspective.")

        round_transcript = []
        # Prompt each stakeholder individually
        for persona in personas:
            stakeholder_name = persona["name"]
            role = stakeholder_roles.get(stakeholder_name, "Team Member")
            focus_area = role_focus.get(role, "Focus on general contributions to the decision-making process.")

            # Tailored prompt for each stakeholder
            prompt = (
                "You are Grok-3-Beta, simulating a stakeholder in a human-like, constructive debate for DecisionTwin. "
                f"You are acting as {stakeholder_name}, with the role of {role}. "
                f"Your expertise and focus area: {focus_area}\n"
                "Your characteristics:\n"
                f"- Goals: {', '.join(persona['goals'])}\n"
                f"- Biases: {', '.join(persona['biases'])}\n"
                f"- Tone: {persona['tone']}\n"
                f"- Bio: {persona['bio']}\n"
                f"- Expected Behavior: {persona['expected_behavior']}\n"
                "The debate follows a structured decision-making process, and you are currently in:\n"
                f"- Step: {current_step} (Round {round_num + 1})\n"
                f"- Objective: {objective}\n"
                "You should:\n"
                "- Contribute a 300–400 word response, deeply tied to the dilemma’s specifics and the current process step, from your role’s perspective.\n"
                "- Use Chain-of-Thought reasoning: Think step by step about your goals, biases, tone, bio, and expected negotiation behavior before proposing a solution.\n"
                "- Act proactively, proposing actionable solutions, anticipating challenges, and suggesting innovations within your domain.\n"
                "- **Explicitly reference and build on specific points from the cumulative context**, e.g., 'As [Stakeholder X] noted in Round 1 about [point], I propose...' or 'I disagree with [Stakeholder Y]'s suggestion because...'.\n"
                "- Engage constructively with other stakeholders’ previous arguments, proposing compromises and resolving conflicts.\n"
                "- Consider alternative scenarios or external factors, if provided, when making proposals.\n"
                f"Cumulative Context from Previous Rounds:\n{cumulative_context}\n"
                "Return your response as a single string, representing your statement for this round."
            )

            # Retry logic for API calls
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    completion = client.chat.completions.create(
                        model="grok-3-beta",
                        reasoning_effort="high",
                        messages=[
                            {"role": "system", "content": "You are an AI assistant simulating a stakeholder in a debate."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.8,
                        max_tokens=MAX_TOKENS,
                        timeout=TIMEOUT_S
                    )
                    message = completion.choices[0].message.content.strip()
                    if not message:
                        raise ValueError("Empty response received.")
                    break  # Successful response, exit retry loop
                except Exception as e:
                    print(f"Attempt {attempt + 1} failed for {stakeholder_name} (Round {round_num + 1}): {str(e)}")
                    if attempt == max_retries - 1:  # Last attempt failed
                        # Enhanced fallback response
                        message = (
                            f"As {stakeholder_name}, with the role of {role}, I approach this step with a focus on {focus_area.lower()}. "
                            f"Given my goal to {persona['goals'][0]} and my {persona['tone']} tone, I would emphasize the importance of "
                            f"considering {persona['goals'][0]} in {current_step}. Based on my {persona['biases'][0]}, I might prioritize "
                            f"data or perspectives that align with this goal. However, detailed insights could not be generated due to a persistent error."
                        )
                    else:
                        time.sleep(1)  # Wait before retrying
                        continue

            round_transcript.append({
                "agent": stakeholder_name,
                "round": round_num + 1,
                "step": current_step,
                "message": message
            })

        # Add round contributions to transcript and update cumulative context
        transcript.extend(round_transcript)
        cumulative_context += f"\nRound {round_num + 1} ({current_step}) Contributions:\n"
        for entry in round_transcript:
            cumulative_context += f"- {entry['agent']}: {entry['message']}\n"

    return transcript
