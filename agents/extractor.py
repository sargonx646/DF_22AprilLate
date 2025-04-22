import json
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from config import OPENROUTER_API_KEY, API_URL, MODEL_NAME, TIMEOUT_S, MAX_RETRIES, RETRY_DELAY, MIN_STAKEHOLDERS, MAX_STAKEHOLDERS

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(RETRY_DELAY))
def extract_info(dilemma: str, process_hint: str) -> dict:
    """Extract stakeholders, issues, and process steps from user input using OpenRouter LLM.

    Args:
        dilemma (str): The decision dilemma (e.g., budget allocation).
        process_hint (str): Details about the process or stakeholders.

    Returns:
        dict: JSON with 'stakeholders' (list, 3–7), 'issues', and 'process'.

    Raises:
        ValueError: If API key is missing.
        RuntimeError: If API call or JSON parsing fails.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment.")

    prompt = (
        f"You are an expert in organizational decision-making. Extract {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} key stakeholders, "
        "their interests, biases, and decision-making steps from the provided dilemma and process hint. "
        "Return a JSON object with keys: 'stakeholders' (list of names), 'issues' (list), 'process' (list of steps). "
        "Ensure 'stakeholders' contains exactly 3–7 names. Example:\n"
        "{\n  \"stakeholders\": [\"CEO\", \"CFO\", \"HR\"],\n  \"issues\": [\"Budget constraints\", \"Priority disputes\"],\n"
        "  \"process\": [\"Proposal submission\", \"Debate\", \"Vote\"]\n}\n\n"
        f"Dilemma: {dilemma}\nProcess Hint: {process_hint}"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,  # Balanced creativity and precision
        "max_tokens": 500
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_S)
        response.raise_for_status()
        data = response.json()
        result = json.loads(data["choices"][0]["message"]["content"])

        # Validate output
        if not isinstance(result, dict) or "stakeholders" not in result or len(result["stakeholders"]) < MIN_STAKEHOLDERS or len(result["stakeholders"]) > MAX_STAKEHOLDERS:
            raise ValueError(f"Invalid response: Must include {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} stakeholders.")
        return result
    except (requests.RequestException, json.JSONDecodeError, ValueError) as e:
        raise RuntimeError(f"Extraction failed: {str(e)}")
