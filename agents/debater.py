import json
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from config import OPENROUTER_API_KEY, API_URL, MODEL_NAME, TIMEOUT_S, MAX_RETRIES, RETRY_DELAY, DEBATE_ROUNDS, MAX_TOKENS

def mock_debate(personas: list[dict], rounds: int = DEBATE_ROUNDS) -> list[dict]:
    """Mock debate simulation for testing."""
    print(f"Mocking debate for {len(personas)} personas: {[p['name'] for p in personas]}")
    transcript = []
    for r in range(rounds):
        for p in personas:
            transcript.append({
                "agent": p["name"],
                "message": f"{p['name']} proposes focusing on {p['goals'][0]} in a {p['tone']} tone."
            })
    return transcript

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(RETRY_DELAY))
def simulate_debate(personas: list[dict], rounds: int = DEBATE_ROUNDS) -> list[dict]:
    """Simulate a debate among personas using Grok 3 Mini.

    Args:
        personas: List of persona dictionaries with name, goals, biases, tone.
        rounds: Number of debate rounds.

    Returns:
        List of debate entries with agent and message.
    """
    if not OPENROUTER_API_KEY:
        print("Warning: OPENROUTER_API_KEY not set. Using mock debate.")
        return mock_debate(personas, rounds)

    transcript = []
    for r in range(rounds):
        for persona in personas:
            prompt = (
                f"You are {persona['name']}, a stakeholder with goals: {', '.join(persona['goals'])}, "
                f"biases: {', '.join(persona['biases'])}, and tone: {persona['tone']}. "
                f"In a debate about the decision context, propose an action or perspective "
                f"aligned with your goals in your specified tone. Keep the response concise (50–100 words)."
            )
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7,
                "max_tokens": 150
            }
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_S)
                response.raise_for_status()
                data = response.json()
                print(f"Debate API Response for {persona['name']}: {json.dumps(data, indent=2)}")
                if "choices" not in data or not data["choices"]:
                    print(f"Warning: Invalid API response for {persona['name']}. Using mock message.")
                    transcript.append({
                        "agent": persona["name"],
                        "message": f"{persona['name']} proposes focusing on {persona['goals'][0]} in a {persona['tone']} tone."
                    })
                    continue
                content = data["choices"][0]["message"]["content"].strip()
                transcript.append({
                    "agent": persona["name"],
                    "message": content
                })
            except requests.RequestException as e:
                print(f"API Error for {persona['name']}: {str(e)}, Status: {getattr(e.response, 'status_code', 'N/A')}, Response: {getattr(e.response, 'text', 'N/A')}")
                print(f"Warning: API request failed for {persona['name']}. Using mock message.")
                transcript.append({
                    "agent": persona["name"],
                    "message": f"{persona['name']} proposes focusing on {persona['goals'][0]} in a {persona['tone']} tone."
                })
    return transcript
