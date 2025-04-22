import json
from openai import OpenAI
from typing import List, Dict
from config import DEBATE_ROUNDS, MAX_TOKENS, TIMEOUT_S

def simulate_debate(personas: List[Dict], rounds: int = DEBATE_ROUNDS) -> List[Dict]:
    """
    Simulate a debate among stakeholder personas using xAI's Grok-3-Mini-Beta.

    Args:
        personas (List[Dict]): List of personas with name, goals, biases, and tone.
        rounds (int): Number of debate rounds.

    Returns:
        List[Dict]: Debate transcript with agent and message.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key="xai-RXSTGBf9LckPtkQ6aBySC0LmpdIjqq9fSSK49PcdRvpLHmldwXEuPwlK9n9AsNfXsHps86amuUFE053u"
    )

    transcript = []
    # Initialize conversation history
    messages = [
        {
            "role": "system",
            "content": "You are Grok-3-Mini-Beta, facilitating a debate among stakeholders. Each stakeholder has a name, goals, biases, and tone. Simulate a realistic debate where each stakeholder speaks in their tone, pursues their goals, and reflects their biases. Generate one response per stakeholder per round, ensuring diverse perspectives and constructive dialogue. Return a JSON array of objects with 'agent' (stakeholder name) and 'message' (their statement)."
        },
        {
            "role": "user",
            "content": f"Simulate {rounds} rounds of debate for these stakeholders:\n{json.dumps(personas, indent=2)}\nReturn the transcript as a JSON array."
        }
    ]

    try:
        completion = client.chat.completions.create(
            model="grok-3-mini-beta",
            reasoning_effort="high",
            messages=messages,
            temperature=0.7,
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
                        "message": f"{p['name']} proposes focusing on {p['goals'][0]} in a {p['tone']} tone."
                    })
    except Exception as e:
        print(f"Debate API Error: {str(e)}")
        for r in range(rounds):
            for p in personas:
                transcript.append({
                    "agent": p["name"],
                    "message": f"{p['name']} proposes focusing on {p['goals'][0]} in a {p['tone']} tone."
                })

    return transcript
