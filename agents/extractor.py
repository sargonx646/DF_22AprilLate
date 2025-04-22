import json
import os
from openai import OpenAI
from typing import Dict, List

def extract_info(dilemma: str, process_hint: str, scenarios: str = "") -> Dict:
    """
    Extract decision structure from the provided dilemma, process hint, and alternative scenarios using xAI's Grok-3-Beta.
    Identify and label any assumptions made during extraction.

    Args:
        dilemma (str): The decision context provided by the user.
        process_hint (str): The process and/or stakeholder details provided by the user.
        scenarios (str): Optional alternative scenarios or external factors.

    Returns:
        Dict: Extracted decision structure including decision type, stakeholders, issues, process, and ASCII visualizations.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    prompt = (
        "You are an AI assistant for DecisionTwin for Decision Making, a tool designed to simulate decision-making processes for senior leaders. "
        "Your task is to extract a detailed decision structure from the provided inputs. Consider all inputs: the decision context (dilemma), the process and stakeholder details (process_hint), and any alternative scenarios (scenarios). "
        "Extract the following:\n"
        "1. **Decision Type**: Classify the decision (e.g., Strategic, Tactical, Operational, Other). If unclear, assume based on context and label as 'Assumed'.\n"
        "2. **Stakeholders**: Identify 6–8 stakeholders with:\n"
        "   - Name (e.g., John Doe).\n"
        "   - Role (e.g., CEO, Analyst).\n"
        "   - Psychological Traits (e.g., risk-averse, collaborative).\n"
        "   - Influences (e.g., regulatory bodies, public opinion).\n"
        "   - Biases (e.g., confirmation bias, status quo bias).\n"
        "   - Historical Behavior (e.g., prioritizes short-term gains, consensus-driven).\n"
        "   If stakeholder details are not fully provided, infer them from the context and label as 'Assumed'.\n"
        "3. **Issues**: List 3–5 key issues or priorities (e.g., budget constraints, public safety).\n"
        "4. **Process**: Identify 4–6 process steps (e.g., Assessment, Deliberation), including timeline if provided. If not fully specified, infer and label as 'Assumed'.\n"
        "5. **External Factors**: Extract 2–3 external factors from the scenarios, or infer if not provided, labeling as 'Assumed'.\n"
        "Clearly identify any assumptions made (e.g., 'Assumed: Stakeholder role inferred based on context').\n"
        "Return the results in JSON format with fields 'decision_type', 'stakeholders', 'issues', 'process', and 'external_factors'.\n"
        f"Dilemma:\n{dilemma}\n"
        f"Process Hint:\n{process_hint}\n"
        f"Alternative Scenarios:\n{scenarios}\n"
    )

    try:
        completion = client.chat.completions.create(
            model="grok-3-beta",
            messages=[
                {"role": "system", "content": "You are an AI assistant extracting decision structures."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        result = json.loads(completion.choices[0].message.content)

        # Extracted fields
        decision_type = result.get("decision_type", "Strategic")
        stakeholders = result.get("stakeholders", [])
        issues = result.get("issues", [])
        process = result.get("process", [])
        external_factors = result.get("external_factors", [])

        # Generate ASCII visualizations
        ascii_process = generate_ascii_process(process)
        ascii_stakeholders = generate_ascii_stakeholders(stakeholders)

        return {
            "decision_type": decision_type,
            "stakeholders": stakeholders,
            "issues": issues,
            "process": process,
            "external_factors": external_factors,
            "ascii_process": ascii_process,
            "ascii_stakeholders": ascii_stakeholders
        }
    except Exception as e:
        print(f"Extraction Error: {str(e)}")
        return {
            "decision_type": "Strategic (Assumed due to error)",
            "stakeholders": [{"name": "Unknown", "role": "Unknown", "psychological_traits": "", "influences": "", "biases": "", "historical_behavior": ""}],
            "issues": ["Issue extraction failed"],
            "process": ["Step 1: Assessment (Assumed)", "Step 2: Deliberation (Assumed)"],
            "external_factors": ["External factor extraction failed"],
            "ascii_process": "No process visualization available.",
            "ascii_stakeholders": "No stakeholder visualization available."
        }

def generate_ascii_process(process: List[str]) -> str:
    """
    Generate an ASCII representation of the decision-making process.

    Args:
        process (List[str]): List of process steps.

    Returns:
        str: ASCII representation of the process.
    """
    if not process:
        return "No process steps provided."

    timeline = "===== Decision Process Timeline =====\n"
    for i, step in enumerate(process, 1):
        timeline += f"Step {i}: {step}\n"
        timeline += "  |" + ("-" * 30) + "|\n"
    timeline += "===================================="
    return timeline

def generate_ascii_stakeholders(stakeholders: List[Dict]) -> str:
    """
    Generate an ASCII representation of the stakeholder hierarchy.

    Args:
        stakeholders (List[Dict]): List of stakeholders with name and role.

    Returns:
        str: ASCII representation of the stakeholders.
    """
    if not stakeholders:
        return "No stakeholders provided."

    hierarchy = "===== Stakeholder Hierarchy =====\n"
    for stakeholder in stakeholders:
        name = stakeholder.get("name", "Unknown")
        role = stakeholder.get("role", "Unknown")
        hierarchy += f"{name} ({role})\n"
        hierarchy += "  |" + ("-" * 20) + "|\n"
    hierarchy += "================================"
    return hierarchy
