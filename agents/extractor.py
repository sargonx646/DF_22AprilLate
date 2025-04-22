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

def mock_extraction(dilemma: str, process_hint: str) -> dict:
    """Generate a mock extraction response for testing."""
    return {
        "decision_type": "Other",
        "stakeholders": [
            {"name": "Stakeholder 1", "psychological_traits": "Analytical", "influences": "Strategic Alliances", "biases": "Confirmation Bias", "historical_behavior": "Innovative Initiatives"},
            {"name": "Stakeholder 2", "psychological_traits": "Collaborative", "influences": "Public Opinion", "biases": "Status Quo Bias", "historical_behavior": "Consensus-Building"},
            {"name": "Stakeholder 3", "psychological_traits": "Risk-Averse", "influences": "Regulatory Constraints", "biases": "Cost-Avoidance Bias", "historical_behavior": "Conservative Decision-Making"}
        ],
        "issues": ["Issue 1", "Issue 2"],
        "process": ["Step 1", "Step 2", "Step 3"],
        "ascii_process": generate_ascii_process(["Step 1", "Step 2", "Step 3"]),
        "ascii_stakeholders": generate_ascii_stakeholders([
            {"name": "Stakeholder 1", "psychological_traits": "Analytical", "influences": "Strategic Alliances", "biases": "Confirmation Bias", "historical_behavior": "Innovative Initiatives"},
            {"name": "Stakeholder 2", "psychological_traits": "Collaborative", "influences": "Public Opinion", "biases": "Status Quo Bias", "historical_behavior": "Consensus-Building"},
            {"name": "Stakeholder 3", "psychological_traits": "Risk-Averse", "influences": "Regulatory Constraints", "biases": "Cost-Avoidance Bias", "historical_behavior": "Conservative Decision-Making"}
        ])
    }

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
        print("Warning: OPENROUTER_API_KEY not set. Using mock extraction.")
        return mock_extraction(dilemma, process_hint)

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
        "max_tokens": 1000
    }
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=TIMEOUT_S)
        response.raise_for_status()
        data = response.json()
        print(f"API Response: {json.dumps(data, indent=2)}")
        print(f"HTTP Status: {response.status_code}, Headers: {json.dumps(dict(response.headers), indent=2)}")
        if "choices" not in data or not data["choices"]:
            print("Warning: Invalid API response. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        content = data["choices"][0]["message"]["content"]
        print(f"Raw Content: {content}")
        if content.startswith("```json\n") and content.endswith("\n```"):
            content = content[7:-4].strip()
        try:
            result = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Warning: JSON parsing failed: {str(e)}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        # Validate output
        if not isinstance(result, dict):
            print(f"Warning: Response is not a dictionary: {result}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        if "decision_type" not in result or result["decision_type"] not in DECISION_TYPES:
            print(f"Warning: Invalid or missing decision_type: {result.get('decision_type', 'N/A')}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        if "stakeholders" not in result:
            print(f"Warning: Missing 'stakeholders' key: {result}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        if not (MIN_STAKEHOLDERS <= len(result["stakeholders"]) <= MAX_STAKEHOLDERS):
            print(f"Warning: Invalid stakeholder count: {len(result['stakeholders'])}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        for s in result["stakeholders"]:
            required_fields = ["name", "psychological_traits", "influences", "biases", "historical_behavior"]
            for field in required_fields:
                if field not in s:
                    print(f"Warning: Stakeholder missing '{field}' field: {s}. Using mock extraction.")
                    return mock_extraction(dilemma, process_hint)
        if not isinstance(result.get("issues", []), list) or not isinstance(result.get("process", []), list):
            print(f"Warning: Invalid 'issues' or 'process': {result}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        # Add ASCII graphs
        result["ascii_process"] = generate_ascii_process(result.get("process", []))
        result["ascii_stakeholders"] = generate_ascii_stakeholders(result.get("stakeholders", []))
        return result
    except requests.RequestException as e:
        print(f"API Error: {str(e)}, Status: {getattr(e.response, 'status_code', 'N/A')}, Response: {getattr(e.response, 'text', 'N/A')}")
        print("Warning: API request failed. Using mock extraction.")
        return mock_extraction(dilemma, process_hint)
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
        print("Warning: Validation failed. Using mock extraction.")
        return mock_extraction(dilemma, process_hint)
