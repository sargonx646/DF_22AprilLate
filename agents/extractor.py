import json
import os
from openai import OpenAI
from typing import Dict, List
from config import STAKEHOLDER_ANALYSIS

def extract_info(dilemma: str, process_hint: str, scenarios: str = "") -> Dict:
    """
    Extract a decision structure from user inputs using xAI's Grok-3-Beta. Ensures reliable extraction of at least 4 stakeholders,
    key issues, and process steps, with detailed stakeholder attributes and fallbacks for minimal or vague inputs.

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

    # Enhanced extraction prompt with detailed instructions
    prompt = (
        "You are an AI assistant for DecisionTwin, a user-friendly tool that simulates decision-making processes. "
        "From the inputs below, extract a decision structure. **Always** provide a complete output, even if inputs are vague or minimal, "
        "by making reasonable assumptions and labeling them (e.g., 'Assumed: Generic stakeholder'). Follow these rules:\n"
        "1. **Decision Type**: Identify the decision type (Strategic, Tactical, Operational, Other). Default to 'Strategic' if unclear.\n"
        "2. **Stakeholders**: Extract or generate **at least 4 stakeholders**. For each:\n"
        "   - Name: Use names from the input or generate unique ones (e.g., 'Alex Carter', 'Maria Lopez').\n"
        "   - Role: Identify roles from the input or infer plausible ones (e.g., 'Project Manager', 'Financial Analyst').\n"
        "   - Psychological Traits: Assign one trait (e.g., 'risk-averse', 'analytical') from this list: " + ", ".join(STAKEHOLDER_ANALYSIS['psychological_traits']) + ".\n"
        "   - Influences: Assign one influence (e.g., 'public opinion', 'government policies') from this list: " + ", ".join(STAKEHOLDER_ANALYSIS['influences']) + ".\n"
        "   - Biases: Assign one bias (e.g., 'confirmation bias', 'groupthink') from this list: " + ", ".join(STAKEHOLDER_ANALYSIS['biases']) + ".\n"
        "   - Historical Behavior: Assign one behavior (e.g., 'consensus-driven', 'data-driven') from this list: " + ", ".join(STAKEHOLDER_ANALYSIS['historical_behavior']) + ".\n"
        "   - Bio: Generate a brief bio (50–100 words) based on the role and context, reflecting their professional background.\n"
        "   Label inferred data as '(Inferred by AI)'.\n"
        "3. **Issues**: List 2–3 key issues or priorities. Infer from the dilemma if not explicit.\n"
        "4. **Process**: Define 3–5 process steps. Use input details or default to a basic sequence (e.g., 'Plan', 'Discuss', 'Decide').\n"
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
            temperature=0.5,
            max_tokens=1200,  # Increased for more detailed output
            response_format={"type": "json_object"}
        )
        result = json.loads(completion.choices[0].message.content)

        # Ensure minimum requirements with fallbacks
        decision_type = result.get("decision_type", "Strategic (Assumed)")
        stakeholders = result.get("stakeholders", [])
        
        # Validate and ensure unique stakeholder names and roles
        seen_names = set()
        seen_roles = set()
        unique_stakeholders = []
        for i, s in enumerate(stakeholders):
            name = s.get("name", f"Stakeholder {i+1} (Inferred by AI)")
            role = s.get("role", f"Team Member {i+1} (Inferred by AI)")
            
            # Ensure unique names
            base_name = name.split(" (Inferred by AI)")[0]
            counter = 1
            new_name = base_name
            while new_name in seen_names:
                new_name = f"{base_name} {counter}"
                counter += 1
            if "(Inferred by AI)" in name:
                name = f"{new_name} (Inferred by AI)"
            else:
                name = new_name
            seen_names.add(name)

            # Ensure unique roles
            base_role = role.split(" (Inferred by AI)")[0]
            counter = 1
            new_role = base_role
            while new_role in seen_roles:
                new_role = f"{base_role} {counter}"
                counter += 1
            if "(Inferred by AI)" in role:
                role = f"{new_role} (Inferred by AI)"
            else:
                role = new_role
            seen_roles.add(new_role)

            unique_stakeholders.append({
                "name": name,
                "role": role,
                "psychological_traits": s.get("psychological_traits", f"Analytical (Inferred by AI)"),
                "influences": s.get("influences", f"Public Opinion (Inferred by AI)"),
                "biases": s.get("biases", f"Confirmation Bias (Inferred by AI)"),
                "historical_behavior": s.get("historical_behavior", f"Consensus-Driven (Inferred by AI)"),
                "bio": s.get("bio", f"{name} has extensive experience as a {role.split(' (Inferred by AI)')[0]}, with a focus on strategic decision-making in high-stakes environments. (Inferred by AI)")
            })

        if len(unique_stakeholders) < 4:
            for i in range(4 - len(unique_stakeholders)):
                name = f"Stakeholder {len(unique_stakeholders)+i+1} (Inferred by AI)"
                role = f"Team Member {len(unique_stakeholders)+i+1} (Inferred by AI)"
                unique_stakeholders.append({
                    "name": name,
                    "role": role,
                    "psychological_traits": "Analytical (Inferred by AI)",
                    "influences": "Public Opinion (Inferred by AI)",
                    "biases": "Confirmation Bias (Inferred by AI)",
                    "historical_behavior": "Consensus-Driven (Inferred by AI)",
                    "bio": f"{name} has extensive experience as a {role.split(' (Inferred by AI)')[0]}, with a focus on strategic decision-making in high-stakes environments. (Inferred by AI)"
                })

        issues = result.get("issues", ["Cost (Assumed)", "Time (Assumed)"])
        process = result.get("process", ["Step 1: Plan (Assumed)", "Step 2: Discuss (Assumed)", "Step 3: Decide (Assumed)"])
        external_factors = result.get("external_factors", ["Resource Availability (Assumed)"])

        # Generate ASCII visualizations
        ascii_process = generate_ascii_process(process)
        ascii_stakeholders = generate_ascii_stakeholders(unique_stakeholders)

        return {
            "decision_type": decision_type,
            "stakeholders": unique_stakeholders,
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
                {"name": "Alex Carter (Inferred by AI)", "role": "Manager (Inferred by AI)", "psychological_traits": "Analytical (Inferred by AI)", "influences": "Public Opinion (Inferred by AI)", "biases": "Confirmation Bias (Inferred by AI)", "historical_behavior": "Consensus-Driven (Inferred by AI)", "bio": "Alex Carter has extensive experience as a Manager, with a focus on strategic decision-making in high-stakes environments. (Inferred by AI)"},
                {"name": "Maria Lopez (Inferred by AI)", "role": "Expert (Inferred by AI)", "psychological_traits": "Risk-Averse (Inferred by AI)", "influences": "Government Policies (Inferred by AI)", "biases": "Status Quo Bias (Inferred by AI)", "historical_behavior": "Data-Driven (Inferred by AI)", "bio": "Maria Lopez has extensive experience as an Expert, specializing in policy analysis and risk management. (Inferred by AI)"},
                {"name": "James Kim (Inferred by AI)", "role": "Team Lead (Inferred by AI)", "psychological_traits": "Collaborative (Inferred by AI)", "influences": "Shareholders (Inferred by AI)", "biases": "Optimism Bias (Inferred by AI)", "historical_behavior": "Focuses on Long-Term Strategy (Inferred by AI)", "bio": "James Kim has extensive experience as a Team Lead, known for fostering collaboration and strategic planning. (Inferred by AI)"},
                {"name": "Sarah Patel (Inferred by AI)", "role": "Analyst (Inferred by AI)", "psychological_traits": "Decisive (Inferred by AI)", "influences": "Industry Trends (Inferred by AI)", "biases": "Groupthink (Inferred by AI)", "historical_behavior": "Unilateral Decision-Maker (Inferred by AI)", "bio": "Sarah Patel has extensive experience as an Analyst, with a knack for quick decision-making and trend analysis. (Inferred by AI)"}
            ],
            "issues": ["Cost (Assumed)", "Time (Assumed)"],
            "process": ["Step 1: Plan (Assumed)", "Step 2: Discuss (Assumed)", "Step 3: Decide (Assumed)"],
            "external_factors": ["Resource Availability (Assumed)"],
            "ascii_process": generate_ascii_process(["Step 1: Plan (Assumed)", "Step 2: Discuss (Assumed)", "Step 3: Decide (Assumed)"]),
            "ascii_stakeholders": generate_ascii_stakeholders([
                {"name": "Alex Carter (Inferred by AI)", "role": "Manager (Inferred by AI)"},
                {"name": "Maria Lopez (Inferred by AI)", "role": "Expert (Inferred by AI)"},
                {"name": "James Kim (Inferred by AI)", "role": "Team Lead (Inferred by AI)"},
                {"name": "Sarah Patel (Inferred by AI)", "role": "Analyst (Inferred by AI)"}
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
