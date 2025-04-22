import time
import requests
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from config import OPENROUTER_API_KEY, API_URL, MODEL_NAME, TIMEOUT_S, MAX_RETRIES, RETRY_DELAY, MIN_STAKEHOLDERS, MAX_STAKEHOLDERS, DEBATE_ROUNDS

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(RETRY_DELAY))
def simulate_debate(personas: list[dict], rounds: int = DEBATE_ROUNDS) -> list[dict]:
    """Simulate a round-robin debate among personas using OpenRouter LLM.

    Args:
        personas (list[dict]): List of personas with name, goals, biases, tone.
        rounds (int): Number of debate rounds (default: 3).

    Returns:
        list[dict]: Transcript of debate with agent and message.

    Raises:
        ValueError: If API key is missing or personas are invalid.
        RuntimeError: If API call fails.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set.")
    if not personas or len(personas) < MIN_STAKEHOLDERS or len(personas) > MAX_STAKEHOLDERS:
        raise ValueError(f"{MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} personas required.")

    transcript = []
    for r in range(rounds):
        for p in personas:
            prompt = (
                f"You are {p['name']}, a stakeholder in a budget allocation debate. "
                f"Your goals: {p['goals']}. Biases: {p['biases']}. Tone: {p['tone']}. "
                "Respond to the ongoing discussion in 1–2 sentences, focusing on your goals and biases, "
                f"using your {p['tone']} tone. Recent discussion (last 3 messages):\n{json.dumps(transcript[-3:], indent=2)}\n"
                "Your response:"
            )
            payload = {
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,  # Encourage creative but focused responses
                "max_tokens": 100
            }
            headers = {
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_S)
                response.raise_for_status()
                message = response.json()["choices"][0]["message"]["content"]
                transcript.append({"agent": p["name"], "message": message.strip()})
                time.sleep(0.2)  # Respect OpenRouter rate limits
            except requests.RequestException as e:
                transcript.append({"agent": p["name"], "message": f"[Error: API unavailable - {str(e)}]"})
                time.sleep(0.2)
    return transcript
