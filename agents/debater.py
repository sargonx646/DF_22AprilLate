import json
import os
from openai import OpenAI
from typing import List, Dict
from config import DEBATE_ROUNDS, MAX_TOKENS, TIMEOUT_S

def simulate_debate(personas: List[Dict], dilemma: str, process_hint: str, extracted: Dict, rounds: int = DEBATE_ROUNDS) -> List[Dict]:
    """
    Simulate a human-like, constructive debate among stakeholder personas using xAI's Grok-3-Beta, guided by their personalities and the decision-making process.

    Args:
        personas (List[Dict]): List of personas with name, goals, biases, tone, bio, and expected behavior.
        dilemma (str): The user-provided decision dilemma.
        process_hint (str): The user-provided process and stakeholder details.
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
        process_steps.extend([process_steps[-1]] * (rounds - len(process_steps)))
    process_steps = process_steps[:rounds]

    # Map stakeholders to process steps based on roles
    stakeholder_roles = {}
    for line in process_hint.split("\n"):
        if ":" in line and any(s["name"] in line for s in extracted.get("stakeholders", [])):
            name, role = line.split(":", 1)
            name = name.strip().split(".")[-1].strip()
            role = role.strip()
            stakeholder_roles[name] = role

    step_assignments = {}
    for i, step in enumerate(process_steps):
        step_assignments[i] = []
        for s in extracted.get("stakeholders", []):
            name = s["name"]
            role = stakeholder_roles.get(name, "")
            if i == 0 and ("EAP" in role or "USAID" in role or "F)" in step):  # Situation Assessment
                step_assignments[i].append(name)
            elif i == 1 and ("PM" in role or "EB" in role or "BHA" in role):  # Options Development
                step_assignments[i].append(name)
            elif i == 2 and ("USAID" in role or "DoD" in role or "OMB" in role):  # Interagency Coordination
                step_assignments[i].append(name)
            elif i == 3:  # Task Force Deliberation
                step_assignments[i].append(name)
            elif i == 4 and ("OMB" in role or "Senate" in role):  # Recommendation and Approval
                step_assignments[i].append(name)

    # Initialize cumulative context
    cumulative_context = "Initial Context: The debate begins with the following dilemma and process.\n"
    cumulative_context += f"Dilemma: {dilemma}\nProcess: {process_hint}\n"

    # Simulate debate round by round
    for round_num in range(rounds):
        current_step = process_steps[round_num]
        active_stakeholders = step_assignments[round_num] if step_assignments[round_num] else [p["name"] for p in personas]

        # Generic prompt for the current round
        prompt = (
            "You are Grok-3-Beta, facilitating a human-like, constructive debate among stakeholders at a virtual roundtable. "
            "The debate must follow the decision-making process, with each round corresponding to a specific step. "
            "Stakeholders should act based on their detailed profiles, showing proactivity and human-like reasoning. "
            "For this round:\n"
            f"- Step: {current_step} (Round {round_num + 1})\n"
            f"- Active Stakeholders: {', '.join(active_stakeholders)}\n"
            "Each active stakeholder should:\n"
            "- Contribute a 300–400 word response, deeply tied to the dilemma’s specifics and the current process step.\n"
            "- Base their arguments on their profile: goals, biases, tone, bio (career history, motivations), and expected negotiation behavior.\n"
            "- Act proactively, proposing actionable solutions, anticipating challenges, and suggesting innovations.\n"
            "- Build on the previous step’s outcomes (provided in the cumulative context), ensuring their contribution informs the next step.\n"
            "- Engage constructively with other stakeholders’ previous arguments, referencing their points, resolving conflicts, and collaborating to advance the decision.\n"
            f"Cumulative Context from Previous Rounds:\n{cumulative_context}\n"
            f"Stakeholder Profiles:\n{json.dumps(personas, indent=2)}\n"
            "Return a JSON array of objects with 'agent' (stakeholder name), 'round' (round number), 'step' (process step name), and 'message' (their statement). "
            "Ensure responses are diverse, professional, and reflect a collaborative decision-making process."
        )

        try:
            completion = client.chat.completions.create(
                model="grok-3-beta",
                reasoning_effort="high",
                messages=[
                    {"role": "system", "content": "You are an AI assistant facilitating a human-like debate."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=MAX_TOKENS,
                response_format={"type": "json_object"}
            )
            print(f"Debate Reasoning (Round {round_num + 1}): {completion.choices[0].message.reasoning_content}")
            round_transcript = json.loads(completion.choices[0].message.content)
            if isinstance(round_transcript, list):
                transcript.extend(round_transcript)
            else:
                print(f"Warning: Invalid transcript format for Round {round_num + 1}. Using fallback.")
                for name in active_stakeholders:
                    persona = next(p for p in personas if p["name"] == name)
                    transcript.append({
                        "agent": name,
                        "round": round_num + 1,
                        "step": current_step,
                        "message": f"{name} proposes focusing on {persona['goals'][0]} in a {persona['tone']} tone during {current_step}."
                    })

            # Update cumulative context with this round’s contributions
            cumulative_context += f"\nRound {round_num + 1} ({current_step}) Contributions:\n"
            for entry in round_transcript:
                cumulative_context += f"- {entry['agent']}: {entry['message']}\n"

        except Exception as e:
            print(f"Debate API Error (Round {round_num + 1}): {str(e)}")
            for name in active_stakeholders:
                persona = next(p for p in personas if p["name"] == name)
                transcript.append({
                    "agent": name,
                    "round": round_num + 1,
                    "step": current_step,
                    "message": f"{name} proposes focusing on {persona['goals'][0]} in a {persona['tone']} tone during {current_step}."
                })
            cumulative_context += f"\nRound {round_num + 1} ({current_step}): Error occurred, proceeding with fallback contributions.\n"

    return transcript
