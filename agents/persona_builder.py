import random
from config import MIN_STAKEHOLDERS, MAX_STAKEHOLDERS

def build_personas(stakeholders: list[str]) -> list[dict]:
    """Generate personas for stakeholders with randomized attributes.

    Args:
        stakeholders (list[str]): List of stakeholder names (3–7).

    Returns:
        list[dict]: List of personas with name, goals, biases, and tone.

    Raises:
        ValueError: If stakeholder count is invalid.
    """
    if len(stakeholders) < MIN_STAKEHOLDERS or len(stakeholders) > MAX_STAKEHOLDERS:
        raise ValueError(f"{MIN_STAKEHOLDERS}–{MAX_STAKEHOLDERS} stakeholders required.")

    random.seed(42)  # Ensure reproducible results for testing
    tones = ["analytical", "pragmatic", "emotional", "strategic"]
    biases = ["risk-averse", "pro-growth", "compliance-focused", "cost-conscious"]
    
    return [
        {
            "name": role,
            "goals": [f"Promote {role.lower()}'s priorities in budget allocation"],
            "biases": [random.choice(biases)],
            "tone": random.choice(tones)
        } for role in stakeholders
    ]
