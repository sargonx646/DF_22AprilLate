import requests
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from config import OPENROUTER_API_KEY, API_URL, MODEL_NAME, TIMEOUT_S, MAX_RETRIES, RETRY_DELAY

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(RETRY_DELAY))
def summarize_and_analyze(transcript: list[dict]) -> tuple[str, list[str], str]:
    """Summarize debate, extract keywords, and provide an optimization suggestion.

    Args:
        transcript (list[dict]): Debate transcript with agent and message.

    Returns:
        tuple[str, list[str], str]: Summary, keywords, and optimization suggestion.

    Raises:
        ValueError: If API key is missing.
        RuntimeError: If API call or JSON parsing fails.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set.")
    if not transcript:
        return "", [], ""

    prompt = (
        "You are an expert in organizational analysis. Analyze the provided budget allocation debate transcript. "
        "Summarize the discussion in 2–3 sentences, identify 5–10 key themes as keywords, and provide one actionable "
        "optimization suggestion to improve the decision-making process. "
        "Return JSON with 'summary' (string), 'keywords' (list), and 'suggestion' (string, 1 sentence).\n"
        "Example Output:\n"
        "{\n  \"summary\": \"The debate focused on balancing department needs...\",\n"
        "  \"keywords\": [\"budget\", \"priorities\", \"conflict\", \"resources\", \"strategy\"],\n"
        "  \"suggestion\": \"Increase CFO's input to address cost concerns.\"\n}\n\n"
        f"Debate Transcript:\n{json.dumps(transcript, indent=2)}"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 300
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_S)
        response.raise_for_status()
        data = json.loads(response.json()["choices"][0]["message"]["content"])
        return (
            data.get("summary", ""),
            data.get("keywords", []),
            data.get("suggestion", "")
        )
    except (requests.RequestException, json.JSONDecodeError) as e:
        raise RuntimeError(f"Analysis failed: {str(e)}")
