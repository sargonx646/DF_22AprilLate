import json
import os
from openai import OpenAI
from typing import List, Dict
from config import DEBATE_ROUNDS, MAX_TOKENS, TIMEOUT_S

def simulate_debate(personas: List[Dict], dilemma: str, process_hint: str, extracted: Dict, rounds: int = DEBATE_ROUNDS) -> List[Dict]:
    """
    Simulate a highly relevant, creative, and structured debate among stakeholder personas using xAI's Grok-3-Beta.

    Args:
        personas (List[Dict]): List of personas with name, goals, biases, and tone.
        dilemma (str): The decision dilemma.
        process_hint (str): Process and stakeholder details.
        extracted (Dict): Extracted decision structure with process steps and stakeholder roles.
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
        # Repeat the last step if there aren't enough process steps
        process_steps.extend([process_steps[-1]] * (rounds - len(process_steps)))
    process_steps = process_steps[:rounds]  # Align with number of rounds

    # Map stakeholders to process steps based on roles (from process_hint)
    stakeholder_roles = {}
    for line in process_hint.split("\n"):
        if ":" in line and any(s["name"] in line for s in extracted.get("stakeholders", [])):
            name, role = line.split(":", 1)
            name = name.strip().split(".")[-1].strip()
            role = role.strip()
            stakeholder_roles[name] = role

    # Assign stakeholders to steps based on their roles
    step_assignments = {}
    for i, step in enumerate(process_steps):
        step_assignments[i] = []
        for s in extracted.get("stakeholders", []):
            name = s["name"]
            role = stakeholder_roles.get(name, "")
            # Assign stakeholders to steps based on relevance
            if i == 0 and ("EAP" in role or "USAID" in role or "F)" in step):  # Situation Assessment
                step_assignments[i].append(name)
            elif i == 1 and ("PM" in role or "EB" in role or "BHA" in role):  # Options Development
                step_assignments[i].append(name)
            elif i == 2 and ("USAID" in role or "DoD" in role or "OMB" in role):  # Interagency Coordination
                step_assignments[i].append(name)
            elif i == 3:  # Task Force Deliberation (all stakeholders)
                step_assignments[i].append(name)
            elif i == 4 and ("OMB" in role or "Senate" in role):  # Recommendation and Approval
                step_assignments[i].append(name)

    # Initialize conversation history
    messages = [
        {
            "role": "system",
            "content": (
                "You are Grok-3-Beta, facilitating a highly relevant, creative, and structured debate among stakeholders at a virtual roundtable. "
                "Each stakeholder has a name, goals, biases, tone, psychological traits, influences, and historical behavior. "
                "The debate must follow the decision-making process, with each round corresponding to a specific process step. "
                "Simulate a generative debate where each stakeholder:\n"
                "- Contributes a 300–400 word response per round, deeply tied to the dilemma’s context, extracted issues, and the current process step.\n"
                "- Proposes creative, well-reasoned solutions reflecting their goals, psychological traits (e.g., Analytical, Empathetic), influences (e.g., Political Pressure), and biases (e.g., Confirmation Bias).\n"
                "- Uses their tone (e.g., diplomatic, assertive) and historical behavior (e.g., Consensus-Building) to shape their approach.\n"
                "- Directly engages with other stakeholders’ previous arguments, referencing their points, countering with evidence-based reasoning, or building consensus to advance the discussion.\n"
                "- Focuses on the current process step, ensuring contributions are relevant to the stage (e.g., assessing risks in Situation Assessment, proposing options in Options Development).\n"
                f"The process has {rounds} steps: {', '.join(process_steps)}. "
                "For each round, only the assigned stakeholders should speak, based on their roles:\n"
                + "\n".join([f"Round {i+1} ({process_steps[i]}): {', '.join(step_assignments[i] if step_assignments[i] else ['All stakeholders'])}" for i in range(rounds)]) + "\n"
                "Return a JSON array of objects with 'agent' (stakeholder name), 'round' (round number), 'step' (process step name), and 'message' (their statement). "
                "Ensure responses are diverse, creative, and professional, with stakeholders reasoning together to resolve the dilemma."
            )
        },
        {
            "role": "user",
            "content": (
                f"Dilemma: {dilemma}\n"
                f"Process Hint: {process_hint}\n"
                f"Extracted Structure: {json.dumps(extracted, indent=2)}\n"
                f"Stakeholders: {json.dumps(personas, indent=2)}\n"
                f"Simulate {rounds} rounds of debate, aligned with the process steps. Return the transcript as a JSON array."
            )
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="grok-3-beta",
            reasoning_effort="high",
            messages=messages,
            temperature=0.8,  # Higher for creativity
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        print(f"Debate Reasoning: {completion.choices[0].message.reasoning_content}")
        transcript_data = json.loads(completion.choices[0].message.content)
        if isinstance(transcript_data, list):
            transcript = transcript_data
        else:
            print("Warning: Invalid transcript format. Using fallback.")
            for r in range(rounds):
                for p in personas:
                    transcript.append({
                        "agent": p["name"],
                        "round": r + 1,
                        "step": process_steps[r],
                        "message": f"{p['name']} proposes focusing on {p['goals'][0]} in a {p['tone']} tone, considering {p['biases'][0]} during {process_steps[r]}."
                    })
    except Exception as e:
        print(f"Debate API Error: {str(e)}")
        for r in range(rounds):
            for p in personas:
                transcript.append({
                    "agent": p["name"],
                    "round": r + 1,
                    "step": process_steps[r],
                    "message": f"{p['name']} proposes focusing on {p['goals'][0]} in a {p['tone']} tone, considering {p['biases'][0]} during {process_steps[r]}."
                })

    return transcript
