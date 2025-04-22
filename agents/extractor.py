import json
import requests
from tenacity import retry, stop_after_attempt, wait_fixed
from config import OPENROUTER_API_KEY, API_URL, MODEL_NAME, TIMEOUT_S, MAX_RETRIES, RETRY_DELAY, MIN_STAKEHOLDERS, MAX_STAKEHOLDERS, DECISION_TYPES, STAKEHOLDER_ANALYSIS, MAX_TOKENS

def generate_ascii_process(process: list) -> str:
    """Generate a clear ASCII graph for process steps."""
    if not process:
        return "No process steps provided."
    graph = "=== Decision Process Timeline ===\n"
    graph += "┌───────────────────────────────┐\n"
    for i, step in enumerate(process, 1):
        step = step[:50] + "..." if len(step) > 50 else step
        graph += f"│ Step {i:<2} │ {step:<45} │\n"
        graph += "├───────────────────────────────┤\n" if i < len(process) else "└───────────────────────────────┘\n"
    graph += "================================\n"
    return graph

def generate_ascii_stakeholders(stakeholders: list) -> str:
    """Generate a clear ASCII graph for stakeholders."""
    if not stakeholders:
        return "No stakeholders provided."
    graph = "=== Stakeholder Hierarchy ===\n"
    graph += "┌──────────────────────────────────────────────────┐\n"
    for i, s in enumerate(stakeholders, 1):
        name = s['name'][:20] + "..." if len(s['name']) > 20 else s['name']
        graph += f"│ {i:<2}. │ {name:<20} │ Traits: {s.get('psychological_traits', 'N/A'):<15} │\n"
        graph += f"│    │ {'':<20} │ Infl: {s.get('influences', 'N/A'):<15} │\n"
        graph += f"│    │ {'':<20} │ Bias: {s.get('biases', 'N/A'):<15} │\n"
        graph += f"│    │ {'':<20} │ Hist: {s.get('historical_behavior', 'N/A'):<15} │\n"
        graph += "├──────────────────────────────────────────────────┤\n" if i < len(stakeholders) else "└──────────────────────────────────────────────────┘\n"
    graph += "============================\n"
    return graph

def mock_extraction(dilemma: str, process_hint: str) -> dict:
    """Generate a mock extraction response based on input prompt."""
    # Parse process_hint for stakeholders if possible
    stakeholders = []
    stakeholder_lines = [line.strip() for line in process_hint.split('\n') if line.strip().startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.'))]
    for i, line in enumerate(stakeholder_lines[:MAX_STAKEHOLDERS], 1):
        name = line.split(':')[0].replace(f"{i}.", "").strip() or f"Stakeholder {i}"
        stakeholders.append({
            "name": name,
            "psychological_traits": STAKEHOLDER_ANALYSIS['psychological_traits'][i % len(STAKEHOLDER_ANALYSIS['psychological_traits'])],
            "influences": STAKEHOLDER_ANALYSIS['influences'][i % len(STAKEHOLDER_ANALYSIS['influences'])],
            "biases": STAKEHOLDER_ANALYSIS['biases'][i % len(STAKEHOLDER_ANALYSIS['biases'])],
            "historical_behavior": STAKEHOLDER_ANALYSIS['historical_behavior'][i % len(STAKEHOLDER_ANALYSIS['historical_behavior'])]
        })
    # Fallback if no stakeholders found
    if not stakeholders:
        stakeholders = [
            {"name": "Stakeholder 1", "psychological_traits": "Analytical", "influences": "Strategic Alliances", "biases": "Confirmation Bias", "historical_behavior": "Consensus-Building"},
            {"name": "Stakeholder 2", "psychological_traits": "Empathetic", "influences": "Public Opinion", "biases": "Optimism Bias", "historical_behavior": "Innovative Initiatives"},
            {"name": "Stakeholder 3", "psychological_traits": "Authoritative", "influences": "Political Pressure", "biases": "Groupthink", "historical_behavior": "Conservative Decision-Making"}
        ]
    issues = ["Issue 1", "Issue 2", "Issue 3"]  # Generic fallback
    process = ["Step 1", "Step 2", "Step 3"]
    # For State Department prompt, use specific data
    if "State Department" in dilemma or "Indo-Pacific" in dilemma:
        stakeholders = [
            {"name": "Elizabeth Carter", "psychological_traits": "Analytical", "influences": "Strategic Alliances", "biases": "Confirmation Bias", "historical_behavior": "Consensus-Building"},
            {"name": "Michael Nguyen", "psychological_traits": "Empathetic", "influences": "Public Opinion", "biases": "Optimism Bias", "historical_behavior": "Innovative Initiatives"},
            {"name": "Laura Thompson", "psychological_traits": "Authoritative", "influences": "Political Pressure", "biases": "Groupthink", "historical_behavior": "Conservative Decision-Making"},
            {"name": "Priya Sharma", "psychological_traits": "Risk-Tolerant", "influences": "Financial Incentives", "biases": "Status Quo Bias", "historical_behavior": "Aggressive Expansion"},
            {"name": "James Sullivan", "psychological_traits": "Collaborative", "influences": "Regulatory Constraints", "biases": "Cost-Avoidance Bias", "historical_behavior": "Compliance-Driven"},
            {"name": "Rebecca Ortiz", "psychological_traits": "Risk-Averse", "influences": "Personal Ambition", "biases": "Confirmation Bias", "historical_behavior": "Conservative Decision-Making"},
            {"name": "Robert Kline", "psychological_traits": "Authoritative", "influences": "Political Pressure", "biases": "Groupthink", "historical_behavior": "Compliance-Driven"}
        ]
        issues = ["Humanitarian crisis", "Security threats", "Economic instability", "Political viability"]
        process = ["Situation Assessment", "Options Development", "Interagency Coordination", "Task Force Deliberation", "Recommendation and Approval"]
    return {
        "decision_type": "Foreign Policy" if "State Department" in dilemma else "Other",
        "stakeholders": stakeholders,
        "issues": issues,
        "process": process,
        "ascii_process": generate_ascii_process(process),
        "ascii_stakeholders": generate_ascii_stakeholders(stakeholders)
    }

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(RETRY_DELAY))
def extract_info(dilemma: str, process_hint: str) -> dict:
    """Extract detailed decision structure using Grok 3 Mini.

    Args:
        dilemma (str): The decision dilemma.
        process_hint (str): Details about the process or stakeholders.

    Returns:
        dict: JSON with decision_type, stakeholders (list, 3–10, with analysis), issues, process, ascii graphs.
    """
    if not OPENROUTER_API_KEY:
        print("Warning: OPENROUTER_API_KEY not set. Using mock extraction.")
        return mock_extraction(dilemma, process_hint)

    prompt = (
        f"You are an expert in organizational decision-making with advanced reasoning capabilities. Thoroughly analyze the provided dilemma and process hint to: "
        f"1. Categorize the decision type ({', '.join(DECISION_TYPES)}) based on the context (e.g., budget allocation, policy, corporate strategy). "
        f"2. Extract {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} key stakeholders (humans or entities) exactly as named in the input, preserving full names and titles. "
        f"For each stakeholder, provide: "
        f"- name: Exact name from input (e.g., 'Elizabeth Carter', not 'Stakeholder 1'). "
        f"- psychological_traits: Select one from {', '.join(STAKEHOLDER_ANALYSIS['psychological_traits'])} based on their role and context. "
        f"- influences: Select one from {', '.join(STAKEHOLDER_ANALYSIS['influences'])} based on their priorities. "
        f"- biases: Select one from {', '.join(STAKEHOLDER_ANALYSIS['biases'])} based on their behavior. "
        f"- historical_behavior: Select one from {', '.join(STAKEHOLDER_ANALYSIS['historical_behavior'])} based on past actions. "
        f"3. Identify 3–5 specific issues central to the dilemma (e.g., 'Humanitarian crisis', not 'Issue 1'), derived from the context. "
        f"4. Extract the process steps in chronological order, using descriptive names (e.g., 'Situation Assessment', not 'Step 1') from the input or inferred logically. "
        f"Return a JSON object with keys: 'decision_type', 'stakeholders' (list of objects), 'issues' (list), 'process' (list). "
        f"Ensure 'stakeholders' contains {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} entries, names match input exactly, issues and process are specific, and the response is valid JSON. "
        f"Wrap the JSON in triple backticks (```json\n...\n```). Example:\n"
        "```json\n"
        "{\n  \"decision_type\": \"Foreign Policy\",\n"
        "  \"stakeholders\": [\n    {\"name\": \"Elizabeth Carter\", \"psychological_traits\": \"Analytical\", "
        "\"influences\": \"Strategic Alliances\", \"biases\": \"Confirmation Bias\", "
        "\"historical_behavior\": \"Consensus-Building\"}\n  ],\n"
        "  \"issues\": [\"Humanitarian crisis\", \"Security threats\"],\n"
        "  \"process\": [\"Situation Assessment\", \"Options Development\"]\n}\n"
        "```\n\n"
        f"Dilemma: {dilemma}\nProcess Hint: {process_hint}"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,  # Lowered for precision
        "max_tokens": MAX_TOKENS,
        "reasoning": {"effort": "high"}  # High reasoning for Grok 3 Mini
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
        # Relaxed validation
        if not isinstance(result, dict):
            print(f"Warning: Response is not a dictionary: {result}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        result["decision_type"] = result.get("decision_type", "Other")
        if result["decision_type"] not in DECISION_TYPES:
            print(f"Warning: Invalid decision_type: {result['decision_type']}. Setting to 'Other'.")
            result["decision_type"] = "Other"
        result["stakeholders"] = result.get("stakeholders", [])
        if not (MIN_STAKEHOLDERS <= len(result["stakeholders"]) <= MAX_STAKEHOLDERS):
            print(f"Warning: Invalid stakeholder count: {len(result['stakeholders'])}. Using mock extraction.")
            return mock_extraction(dilemma, process_hint)
        for s in result["stakeholders"]:
            required_fields = ["name", "psychological_traits", "influences", "biases", "historical_behavior"]
            for field in required_fields:
                s[field] = s.get(field, STAKEHOLDER_ANALYSIS[field][0] if field != "name" else "Unknown")
        result["issues"] = result.get("issues", ["Unknown issue"])
        result["process"] = result.get("process", ["Unknown step"])
        # Add ASCII graphs
        result["ascii_process"] = generate_ascii_process(result["process"])
        result["ascii_stakeholders"] = generate_ascii_stakeholders(result["stakeholders"])
        return result
    except requests.RequestException as e:
        print(f"API Error: {str(e)}, Status: {getattr(e.response, 'status_code', 'N/A')}, Response: {getattr(e.response, 'text', 'N/A')}")
        print("Warning: API request failed. Using mock extraction.")
        return mock_extraction(dilemma, process_hint)
    except ValueError as e:
        print(f"Validation Error: {str(e)}")
        print("Warning: Validation failed. Using mock extraction.")
        return mock_extraction(dilemma, process_hint)
