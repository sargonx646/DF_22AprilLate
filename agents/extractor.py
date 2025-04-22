import json
import re
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_fixed
from config import DECISION_TYPES, STAKEHOLDER_ANALYSIS, MIN_STAKEHOLDERS, MAX_STAKEHOLDERS, TIMEOUT_S, MAX_RETRIES, RETRY_DELAY, MAX_TOKENS

def generate_ascii_process(process: list) -> str:
    """Generate a clear ASCII graph for process steps."""
    if not process:
        return "No process steps provided."
    graph = "=== Decision Process Timeline ===\n"
    graph += "┌────┬──────────────────────────────────────────────────┐\n"
    graph += "│ No │ Step Description                                 │\n"
    graph += "├────┼──────────────────────────────────────────────────┤\n"
    for i, step in enumerate(process, 1):
        step = step[:45] + "..." if len(step) > 45 else step.ljust(45)
        graph += f"│ {i:<2} │ {step} │\n"
    graph += "└────┴──────────────────────────────────────────────────┘\n"
    graph += "================================\n"
    return graph

def generate_ascii_stakeholders(stakeholders: list) -> str:
    """Generate a clear ASCII graph for stakeholders."""
    if not stakeholders:
        return "No stakeholders provided."
    graph = "=== Stakeholder Hierarchy ===\n"
    graph += "┌────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┬────────────────────┐\n"
    graph += "│ No │ Name               │ Traits             │ Influences         │ Biases             │ History            │\n"
    graph += "├────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┼────────────────────┤\n"
    for i, s in enumerate(stakeholders, 1):
        name = s['name'][:18] + "..." if len(s['name']) > 18 else s['name'].ljust(18)
        traits = s.get('psychological_traits', 'N/A')[:18].ljust(18)
        infl = s.get('influences', 'N/A')[:18].ljust(18)
        biases = s.get('biases', 'N/A')[:18].ljust(18)
        hist = s.get('historical_behavior', 'N/A')[:18].ljust(18)
        graph += f"│ {i:<2} │ {name} │ {traits} │ {infl} │ {biases} │ {hist} │\n"
    graph += "└────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┴────────────────────┘\n"
    graph += "============================\n"
    return graph

def mock_extraction(dilemma: str, process_hint: str) -> dict:
    """Generate a mock extraction response based on input prompt."""
    stakeholders = []
    stakeholder_pattern = r'(\d+\.\s+[\w\s,]+?:.*?)(?=\n\d+\.|$)'  # Match numbered stakeholder lines
    matches = re.findall(stakeholder_pattern, process_hint, re.DOTALL)
    for i, match in enumerate(matches[:MAX_STAKEHOLDERS], 1):
        name = match.split(':')[0].strip().replace(f"{i}.", "").strip()
        if not name:
            name = f"Stakeholder {i}"
        description = match.split(':')[1].strip() if ':' in match else ""
        traits = "Analytical" if "strategy" in description.lower() else "Empathetic" if "humanitarian" in description.lower() else STAKEHOLDER_ANALYSIS['psychological_traits'][i % len(STAKEHOLDER_ANALYSIS['psychological_traits'])]
        stakeholders.append({
            "name": name,
            "psychological_traits": traits,
            "influences": STAKEHOLDER_ANALYSIS['influences'][i % len(STAKEHOLDER_ANALYSIS['influences'])],
            "biases": STAKEHOLDER_ANALYSIS['biases'][i % len(STAKEHOLDER_ANALYSIS['biases'])],
            "historical_behavior": STAKEHOLDER_ANALYSIS['historical_behavior'][i % len(STAKEHOLDER_ANALYSIS['historical_behavior'])]
        })
    issue_pattern = r'(\d+\.\s+.*?)(?=\n\d+\.|$)'  # Match numbered challenges
    issues = [match.strip().split(':')[0].strip().replace(f"{i+1}.", "").strip() for i, match in enumerate(re.findall(issue_pattern, dilemma, re.DOTALL))]
    if not issues:
        issues = ["Unknown issue 1", "Unknown issue 2", "Unknown issue 3"]
    process_pattern = r'(\d+\.\s+.*?)(?=\n\d+\.|$)'  # Match numbered steps
    process = [match.strip().split(':')[0].strip().replace(f"{i+1}.", "").strip() for i, match in enumerate(re.findall(process_pattern, process_hint, re.DOTALL))]
    if not process:
        process = ["Unknown step 1", "Unknown step 2", "Unknown step 3"]
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
        issues = ["Humanitarian crisis in Country A", "Security threats in Country B", "Economic instability in Country C", "Political viability"]
        process = ["Situation Assessment", "Options Development", "Interagency Coordination", "Task Force Deliberation", "Recommendation and Approval"]
    return {
        "decision_type": "Foreign Policy" if "State Department" in dilemma else "Other",
        "stakeholders": stakeholders,
        "issues": issues[:5],
        "process": process,
        "ascii_process": generate_ascii_process(process),
        "ascii_stakeholders": generate_ascii_stakeholders(stakeholders)
    }

@retry(stop=stop_after_attempt(MAX_RETRIES), wait=wait_fixed(RETRY_DELAY))
def extract_info(dilemma: str, process_hint: str) -> dict:
    """Extract detailed decision structure using xAI's Grok-3-Mini-Beta.

    Args:
        dilemma (str): The decision dilemma.
        process_hint (str): Details about the process or stakeholders.

    Returns:
        dict: JSON with decision_type, stakeholders (list, 3–10, with analysis), issues, process, ascii graphs.
    """
    # Initialize xAI API client
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key="xai-RXSTGBf9LckPtkQ6aBySC0LmpdIjqq9fSSK49PcdRvpLHmldwXEuPwlK9n9AsNfXsHps86amuUFE053u"
    )

    prompt = (
        f"You are Grok-3-Mini-Beta, an advanced AI specializing in organizational decision-making. Your task is to deeply analyze the provided dilemma and process hint to extract a precise decision framework. Follow these instructions carefully:\n"
        f"1. **Decision Type**: Determine the decision type from {', '.join(DECISION_TYPES)} by analyzing the dilemma’s context. "
        f"For example, select 'Foreign Policy' for international aid allocation, 'Corporate Strategy' for business investments, or 'Other' if unclear.\n"
        f"2. **Stakeholders**: Identify {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} stakeholders, which are specific individuals (e.g., 'Elizabeth Carter') or entities (e.g., 'USAID') explicitly named in the process hint. "
        f"Extract their full names exactly as provided, preserving titles and avoiding generic terms like 'Stakeholder 1'. "
        f"For each stakeholder, infer attributes based on their role, description, or priorities in the process hint:\n"
        f"- psychological_traits: Select one from {', '.join(STAKEHOLDER_ANALYSIS['psychological_traits'])} (e.g., 'Empathetic' for humanitarian advocates, 'Analytical' for strategic planners).\n"
        f"- influences: Select one from {', '.join(STAKEHOLDER_ANALYSIS['influences'])} (e.g., 'Political Pressure' for government officials, 'Financial Incentives' for business leaders).\n"
        f"- biases: Select one from {', '.join(STAKEHOLDER_ANALYSIS['biases'])} (e.g., 'Groupthink' for consensus-driven, 'Confirmation Bias' for entrenched views).\n"
        f"- historical_behavior: Select one from {', '.join(STAKEHOLDER_ANALYSIS['historical_behavior'])} (e.g., 'Compliance-Driven' for regulatory focus, 'Innovative Initiatives' for reformists).\n"
        f"If the process hint lacks explicit stakeholders, infer plausible stakeholders from the context, ensuring they are specific entities or roles.\n"
        f"3. **Issues**: Extract 3–5 specific issues directly from the dilemma’s challenges, avoiding generic terms like 'Issue 1'. "
        f"For example, for a dilemma about regional stabilization, issues might include 'Humanitarian crisis in Country A', 'Security threats in Country B', 'Economic instability in Country C'.\n"
        f"4. **Process Steps**: Extract the decision-making process steps in chronological order from the process hint, using descriptive names (e.g., 'Situation Assessment', not 'Step 1'). "
        f"If steps are not explicitly listed, infer 3–5 logical steps based on the context (e.g., assessment, planning, coordination, decision). Ensure steps reflect the timeline or structure provided.\n"
        f"Return a JSON object with keys: 'decision_type', 'stakeholders' (list of objects), 'issues' (list), 'process' (list). "
        f"Ensure 'stakeholders' has {MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} entries, names match the input exactly, issues and process are specific, and the response is valid JSON. "
        f"Wrap the JSON in triple backticks (```json\n...\n```). Example:\n"
        "```json\n"
        "{\n  \"decision_type\": \"Foreign Policy\",\n"
        "  \"stakeholders\": [\n    {\"name\": \"Elizabeth Carter\", \"psychological_traits\": \"Analytical\", "
        "\"influences\": \"Strategic Alliances\", \"biases\": \"Confirmation Bias\", "
        "\"historical_behavior\": \"Consensus-Building\"},\n    {\"name\": \"USAID\", \"psychological_traits\": \"Collaborative\", "
        "\"influences\": \"Public Opinion\", \"biases\": \"Optimism Bias\", \"historical_behavior\": \"Innovative Initiatives\"}\n  ],\n"
        "  \"issues\": [\"Humanitarian crisis in Country A\", \"Security threats in Country B\", \"Economic instability in Country C\"],\n"
        "  \"process\": [\"Situation Assessment\", \"Options Development\", \"Interagency Coordination\", \"Task Force Deliberation\", \"Recommendation and Approval\"]\n}\n"
        "```\n\n"
        f"Dilemma: {dilemma}\nProcess Hint: {process_hint}"
    )

    try:
        completion = client.chat.completions.create(
            model="grok-3-mini-beta",
            reasoning_effort="high",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        print(f"Extraction Reasoning: {completion.choices[0].message.reasoning_content}")
        content = completion.choices[0].message.content
        if content.startswith("```json\n") and content.endswith("\n```"):
            content = content[7:-4].strip()
        result = json.loads(content)
        
        # Validation
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
            if s["name"] != "Unknown" and s["name"] not in process_hint:
                print(f"Warning: Stakeholder name '{s['name']}' not found in process_hint. Using mock extraction.")
                return mock_extraction(dilemma, process_hint)
        result["issues"] = result.get("issues", ["Unknown issue"])
        result["process"] = result.get("process", ["Unknown step"])
        result["ascii_process"] = generate_ascii_process(result["process"])
        result["ascii_stakeholders"] = generate_ascii_stakeholders(result["stakeholders"])
        return result
    except Exception as e:
        print(f"API Error: {str(e)}")
        print("Warning: API request failed. Using mock extraction.")
        return mock_extraction(dilemma, process_hint)
