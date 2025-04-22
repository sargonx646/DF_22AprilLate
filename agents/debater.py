import json
import os
from openai import OpenAI
from typing import List, Dict
from config import DEBATE_ROUNDS, MAX_TOKENS, TIMEOUT_S

def simulate_debate(personas: List[Dict], dilemma: str, process_hint: str, extracted: Dict, rounds: int = DEBATE_ROUNDS) -> List[Dict]:
    """
    Simulate a creative and context-aware debate among stakeholder personas using xAI's Grok-3-Mini-Beta.

    Args:
        personas (List[Dict]): List of personas with name, goals, biases, and tone.
        dilemma (str): The decision dilemma.
        process_hint (str): Process and stakeholder details.
        extracted (Dict): Extracted decision structure.
        rounds (int): Number of debate rounds.

    Returns:
        List[Dict]: Debate transcript with agent and message.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    transcript = []
    # Initialize conversation history
    messages = [
        {
            "role": "system",
            "content": (
                "You are Grok-3-Mini-Beta, facilitating a highly creative and meaningful debate among stakeholders at a virtual roundtable. "
                "Each stakeholder has a name, goals, biases, tone, psychological traits, influences, and historical behavior. "
                "Simulate a dynamic, context-aware debate where each stakeholder:\n"
                "- Proposes specific, innovative solutions aligned with their goals and the dilemma’s context.\n"
                "- Reflects their psychological traits (e.g., Analytical, Empathetic), influences (e.g., Political Pressure), and biases (e.g., Confirmation Bias).\n"
                "- Uses their tone (e.g., diplomatic, assertive) and considers their historical behavior (e.g., Consensus-Building).\n"
                "- Critically engages with others’ proposals, countering or building on them to advance the discussion.\n"
                "- Focuses on the dilemma’s issues and process steps, ensuring discussions are substantive and meaningful.\n"
                f"Generate {rounds} rounds, with each stakeholder contributing a 50–70 word response per round. "
                "Return a JSON array of objects with 'agent' (stakeholder name) and 'message' (their statement). "
                "Ensure diversity in perspectives, avoid repetition, and maintain a professional yet engaging tone."
            )
        },
        {
            "role": "user",
            "content": (
                f"Dilemma: {dilemma}\n"
                f"Process Hint: {process_hint}\n"
                f"Extracted Structure: {json.dumps(extracted, indent=2)}\n"
                f"Stakeholders: {json.dumps(personas, indent=2)}\n"
                f"Simulate {rounds} rounds of debate. Return the transcript as a JSON array."
            )
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="grok-3-mini-beta",
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
                        "message": f"{p['name']} proposes focusing on {p['goals'][0]} in a {p['tone']} tone, considering {p['biases'][0]}."
                    })
    except Exception as e:
        print(f"Debate API Error: {str(e)}")
        for r in range(rounds):
            for p in personas:
                transcript.append({
                    "agent": p["name"],
                    "message": f"{p['name']} proposes focusing on {p['goals'][0]} in a {p['tone']} tone, considering {p['biases'][0]}."
                })

    return transcript
