import json
import os
from openai import OpenAI
from typing import Dict, List

def extract_info(dilemma: str, process_hint: str, scenarios: str = "") -> Dict:
    """
    Extract a decision structure from user inputs using xAI's Grok-3-Beta. Ensures reliable extraction of at least 4 stakeholders,
    key issues, and process steps, with fallbacks for minimal or vague inputs.

    Args:
        dilemma (str): The decision context provided by the user.
        process_hint (str): Details about the process and/or stakeholders.
        scenarios (str): Optional alternative scenarios or external factors.

    Returns:
        Dict: Extracted decision structure with decision type, stakeholders, issues, process, external factors, and ASCII visuals.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    # Robust, directive extraction prompt
    prompt = (
        "You are an AI assistant for DecisionTwin, a user-friendly tool that simulates decision-making processes. "
        "From the inputs below, extract a decision structure. **Always** provide a complete output, even if inputs are vague or minimal, "
        "by making reasonable assumptions and labeling them (e.g., 'Assumed: Generic stakeholder'). Follow these rules:\n"
        "1. **Decision Type**: Identify the decision type (Strategic, Tactical, Operational, Other). Default to 'Strategic' if unclear.\n"
        "2. **Stakeholders**: Extract or generate **at least 4 stakeholders**. For each:\n"
        "   - Name: Use names from the input or generate generic ones (e.g., 'Stakeholder 1').\n"
        "   - Role: Identify roles from the input or infer plausible ones (e.g., 'Manager', 'Expert').\n"
        "3. **Issues**: List 2–3 key issues or priorities. Infer from the dilemma if not explicit.\n"
        "4. **Process**: Define 3 process steps. Use input details or default to a basic sequence (e.g., 'Plan', 'Discuss', 'Decide').\n"
        "5. **External Factors**: Extract 1–2 factors from scenarios, or assume generic ones if absent.\n"
        "Return the result in JSON format with fields: 'decision_type', 'stakeholders', 'issues', 'process', 'external_factors'.\n"
        "Inputs:\n"
        f"- Dilemma: {dilemma}\n"
        f"- Process Hint: {process_hint}\n"
        f"- Scenarios: {scenarios}\n"
    )

    try:
        completion = client.chat.completions.create(
            model="grok-3-beta",
            messages=[
                {"role": "system", "content": "You are an AI assistant extracting decision structures."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,  # Lowered for consistency
            max_tokens=800,
            response_format={"type": "json_object"}
        )
        result = json.loads(completion.choices[0].message.content)

        # Ensure minimum requirements with fallbacks
        decision_type = result.get("decision_type", "Strategic (Assumed)")
        stakeholders = result.get("stakeholders", [])
        if len(stakeholders) < 4:
            existing_names = {s.get("name", "") for s in stakeholders}
            for i in range(4 - len(stakeholders)):
                name = f"Stakeholder {i+1} (Assumed)" if f"Stakeholder {i+1}" not in existing_names else f"Team Member {i+1} (Assumed)"
                stakeholders.append({"name": name, "role": "Team Member (Assumed)"})
        issues = result.get("issues", ["Cost (Assumed)", "Time (Assumed)"])
        process = result.get("process", ["Step 1: Plan (Assumed)", "Step 2: Discuss (Assumed)", "Step 3: Decide (Assumed)"])
        external_factors = result.get("external_factors", ["Resource Availability (Assumed)"])

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
        # Hardcoded fallback for reliability
        return {
            "decision_type": "Strategic (Assumed due to error)",
            "stakeholders": [
                {"name": "Stakeholder 1 (Assumed)", "role": "Manager (Assumed)"},
                {"name": "Stakeholder 2 (Assumed)", "role": "Expert (Assumed)"},
                {"name": "Stakeholder 3 (Assumed)", "role": "Team Lead (Assumed)"},
                {"name": "Stakeholder 4 (Assumed)", "role": "Analyst (Assumed)"}
            ],
            "issues": ["Cost (Assumed)", "Time (Assumed)"],
            "process": ["Step 1: Plan (Assumed)", "Step 2: Discuss (Assumed)", "Step 3: Decide (Assumed)"],
            "external_factors": ["Resource Availability (Assumed)"],
            "ascii_process": generate_ascii_process(["Step 1: Plan (Assumed)", "Step 2: Discuss (Assumed)", "Step 3: Decide (Assumed)"]),
            "ascii_stakeholders": generate_ascii_stakeholders([
                {"name": "Stakeholder 1 (Assumed)", "role": "Manager (Assumed)"},
                {"name": "Stakeholder 2 (Assumed)", "role": "Expert (Assumed)"},
                {"name": "Stakeholder 3 (Assumed)", "role": "Team Lead (Assumed)"},
                {"name": "Stakeholder 4 (Assumed)", "role": "Analyst (Assumed)"}
            ])
        }

def generate_ascii_process(process: List[str]) -> str:
    """
    Generate an ASCII representation of the decision-making process.
    """
    if not process:
        return "No process steps available."
    timeline = "=== Process Timeline ===\n"
    for i, step in enumerate(process, 1):
        timeline += f"{i}. {step}\n"
    timeline += "======================="
    return timeline

def generate_ascii_stakeholders(stakeholders: List[Dict]) -> str:
    """
    Generate an ASCII representation of the stakeholder hierarchy.
    """
    if not stakeholders:
        return "No stakeholders available."
    hierarchy = "=== Stakeholders ===\n"
    for s in stakeholders:
        name = s.get("name", "Unknown")
        role = s.get("role", "Unknown")
        hierarchy += f"- {name} ({role})\n"
    hierarchy += "==================="
    return hierarchy
