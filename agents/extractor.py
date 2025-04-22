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
        ValueError: If API key is missing or response is invalid.
        RuntimeError: If API call or JSON parsing fails.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment.")

    prompt = (
        f"You are an expert in organizational decision-making. Extract {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} key stakeholders, "
        "their interests, biases, and decision-making steps from the provided dilemma and process hint. "
        "Return a JSON object with keys: 'stakeholders' (list of names), 'issues' (list), 'process' (list of steps). "
        "Ensure 'stakeholders' contains exactly 3–7 names and the response is valid JSON. "
        "Wrap the JSON in triple backticks (```json\n...\n```). Example:\n"
        "```json\n"
        "{\n  \"stakeholders\": [\"CEO\", \"CFO\", \"HR\"],\n  \"issues\": [\"Budget constraints\", \"Priority disputes\"],\n"
        "  \"process\": [\"Proposal submission\", \"Debate\", \"Vote\"]\n}\n"
        "```\n\n"
        f"Dilemma: {dilemma}\nProcess Hint: {process_hint}"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
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
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"Invalid API response: 'choices' missing or empty. Response: {json.dumps(data, indent=2)}")
        content = data["choices"][0]["message"]["content"]
        # Extract JSON from ```json\n...\n``` block
        if content.startswith("```json\n") and content.endswith("\n```"):
            content = content[7:-4].strip()
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse API response as JSON: {str(e)}. Raw content: {content}")
        # Validate output
        if not isinstance(result, dict):
            raise ValueError(f"API response is not a dictionary. Parsed content: {result}")
        if "stakeholders" not in result:
            raise ValueError(f"API response missing 'stakeholders' key. Parsed content: {result}")
        if not (MIN_STAKEHOLDERS <= len(result["stakeholders"]) <= MAX_STAKEHOLDERS):
            raise ValueError(f"Invalid stakeholder count: {len(result['stakeholders'])}. Must be {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS}. Parsed content: {result}")
        if not isinstance(result.get("issues", []), list) or not isinstance(result.get("process", []), list):
            raise ValueError(f"Invalid response: 'issues' or 'process' is not a list. Parsed content: {result}")
        return result
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}. Status code: {getattr(e.response, 'status_code', 'N/A')}, Response: {getattr(e.response, 'text', 'N/A')}")
    except ValueError as e:
        raise ValueError(f"Validation error: {str(e)}")
