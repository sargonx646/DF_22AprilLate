import json
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from config import OPENROUTER_API_KEY, API_URL, MODEL_NAME, TIMEOUT_S, MAX_RETRIES, RETRY_DELAY, MIN_STAKEHOLDERS, MAX_STAKEHOLDERS, DECISION_TYPES, STAKEHOLDER_ANALYSIS

def generate_ascii_process(process: list) -> str:
    """Generate an ASCII graph for the process steps."""
    if not process:
        return "No process steps provided."
    graph = "=== Decision Process Timeline ===\n"
    for i, step in enumerate(process, 1):
        graph += f"Step {i}: {'-' * (20 - len(str(i)))} {step}\n"
    graph += "================================\n"
    return graph

def generate_ascii_stakeholders(stakeholders: list) -> str:
    """Generate an ASCII graph for stakeholders."""
    if not stakeholders:
        return "No stakeholders provided."
    graph = "=== Stakeholder Hierarchy ===\n"
    for i, stakeholder in enumerate(stakeholders, 1):
        graph += f"{i}. {stakeholder['name']}\n"
        graph += f"   |--- Traits: {stakeholder.get('psychological_traits', 'N/A')}\n"
        graph += f"   |--- Influences: {stakeholder.get('influences', 'N/A')}\n"
        graph += f"   |--- Biases: {stakeholder.get('biases', 'N/A')}\n"
        graph += f"   |--- History: {stakeholder.get('historical_behavior', 'N/A')}\n"
    graph += "============================\n"
    return graph

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(RETRY_DELAY))
def extract_info(dilemma: str, process_hint: str) -> dict:
    """Extract detailed decision structure from user input using OpenRouter LLM.

    Args:
        dilemma (str): The decision dilemma.
        process_hint (str): Details about the process or stakeholders.

    Returns:
        dict: JSON with decision_type, stakeholders (list, 3–10, with analysis), issues, process, ascii_process, ascii_stakeholders.

    Raises:
        ValueError: If API key is missing or response is invalid.
        RuntimeError: If API call or JSON parsing fails.
    """
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not set in environment.")

    prompt = (
        f"You are an expert in organizational decision-making. Analyze the provided dilemma and process hint to: "
        f"1. Categorize the decision type ({', '.join(DECISION_TYPES)}). "
        f"2. Extract {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} key stakeholders (humans or entities), including for each: "
        f"- Name, psychological_traits ({', '.join(STAKEHOLDER_ANALYSIS['psychological_traits'])}), "
        f"influences ({', '.join(STAKEHOLDER_ANALYSIS['influences'])}), biases ({', '.join(STAKEHOLDER_ANALYSIS['biases'])}), "
        f"historical_behavior ({', '.join(STAKEHOLDER_ANALYSIS['historical_behavior'])}). "
        f"3. Identify key issues and process steps. "
        f"Return a JSON object with keys: 'decision_type', 'stakeholders' (list of objects), 'issues' (list), 'process' (list). "
        f"Ensure 'stakeholders' contains 3–10 entries and the response is valid JSON. "
        f"Wrap the JSON in triple backticks (```json\n...\n```). Example:\n"
        "```json\n"
        "{\n  \"decision_type\": \"Budget Allocation\",\n"
        "  \"stakeholders\": [\n    {\"name\": \"CEO\", \"psychological_traits\": \"Analytical\", "
        "\"influences\": \"Strategic Alliances\", \"biases\": \"Confirmation Bias\", "
        "\"historical_behavior\": \"Innovative Initiatives\"}\n  ],\n"
        "  \"issues\": [\"Budget constraints\", \"Priority disputes\"],\n"
        "  \"process\": [\"Proposal submission\", \"Debate\", \"Vote\"]\n}\n"
        "```\n\n"
        f"Dilemma: {dilemma}\nProcess Hint: {process_hint}"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000  # Increased for detailed output
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_S)
        response.raise_for_status()
        data = response.json()
        print(f"API Response: {json.dumps(data, indent=2)}")  # Log for debugging
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"Invalid API response: 'choices' missing or empty. Response: {json.dumps(data, indent=2)}")
        content = data["choices"][0]["message"]["content"]
        print(f"Raw Content: {content}")  # Log for debugging
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
        if "decision_type" not in result or result["decision_type"] not in DECISION_TYPES:
            raise ValueError(f"Invalid or missing decision_type. Got: {result.get('decision_type', 'N/A')}")
        if "stakeholders" not in result:
            raise ValueError(f"API response missing 'stakeholders' key. Parsed content: {result}")
        if not (MIN_STAKEHOLDERS <= len(result["stakeholders"]) <= MAX_STAKEHOLDERS):
            raise ValueError(f"Invalid stakeholder count: {len(result['stakeholders'])}. Must be {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS}. Parsed content: {result}")
        for s in result["stakeholders"]:
            required_fields = ["name", "psychological_traits", "influences", "biases", "historical_behavior"]
            for field in required_fields:
                if field not in s:
                    raise ValueError(f"Stakeholder missing '{field}' field: {s}")
        if not isinstance(result.get("issues", []), list) or not isinstance(result.get("process", []), list):
            raise ValueError(f"Invalid response: 'issues' or 'process' is not a list. Parsed content: {result}")
        # Add ASCII graphs
        result["ascii_process"] = generate_ascii_process(result.get("process", []))
        result["ascii_stakeholders"] = generate_ascii_stakeholders(result.get("stakeholders", []))
        return result
    except requests.RequestException as e:
        raise RuntimeError(f"API request failed: {str(e)}. Status code: {getattr(e.response, 'status_code', 'N/A')}, Response: {getattr(e.response, 'text', 'N/A')}")
    except ValueError as e:
        raise ValueError(f"Validation error: {str(e)}")
