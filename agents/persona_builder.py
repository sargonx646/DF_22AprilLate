from typing import List
import random
import os
from openai import OpenAI

def build_personas(names: List[str], dilemma: str, process_hint: str) -> List[dict]:
    """
    Build detailed personas for stakeholders, including AI-generated bios and expected negotiation behaviors,
    based on the user-provided case details.

    Args:
        names (List[str]): List of stakeholder names.
        dilemma (str): The user-provided decision dilemma.
        process_hint (str): The user-provided process and stakeholder details.

    Returns:
        List[dict]: List of personas with name, goals, biases, tone, bio, and expected behavior.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    # Sample attributes for persona generation (as fallback if extraction fails)
    goals_options = [
        "maximize impact",
        "ensure stability",
        "promote growth",
        "maintain oversight",
        "enhance influence",
        "secure resources",
        "minimize risks"
    ]
    biases_options = [
        "confirmation bias",
        "optimism bias",
        "groupthink",
        "status quo bias",
        "cost-avoidance bias"
    ]
    tones = ["diplomatic", "assertive", "empathetic", "analytical", "cautious"]

    personas = []
    for name in names:
        # Basic persona attributes (will be refined by AI)
        goals = random.sample(goals_options, k=2)
        biases = random.sample(biases_options, k=2)
        tone = random.choice(tones)

        # AI-generated Bio and Expected Behavior based on user input
        prompt = (
            f"Generate a detailed bio (150–200 words) and expected negotiation behavior (100–150 words) for a stakeholder named {name}. "
            f"The stakeholder is part of a decision-making process described as follows:\n"
            f"Dilemma: {dilemma}\n"
            f"Process and Stakeholder Details: {process_hint}\n"
            "Infer the stakeholder's role, priorities, career history, personality, and motivations from the provided dilemma and process details. "
            "For example, if the process mentions a role like 'Assistant Secretary, EAP,' infer their focus on regional strategy; if it mentions 'USAID Coordinator,' infer a focus on aid effectiveness. "
            "Incorporate any stakeholder dynamics or conflicts mentioned in the process hint. "
            "For the bio, detail their professional background, key achievements, and personal traits. "
            "For the expected behavior, describe how they’ll negotiate, referencing their goals, biases, tone, and the case specifics (e.g., budget constraints, competing priorities)."
        )

        try:
            completion = client.chat.completions.create(
                model="grok-3-beta",
                messages=[
                    {"role": "system", "content": "You are an AI assistant generating detailed stakeholder profiles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            response = completion.choices[0].message.content
            bio, behavior = response.split("\n\n", 1)  # Split bio and behavior
        except Exception as e:
            print(f"Error generating profile for {name}: {str(e)}")
            bio = f"{name} has a long career in their field, with extensive experience relevant to the decision at hand. They are known for their dedication and strategic thinking."
            behavior = f"During negotiations, {name} will focus on their primary goals, advocating strongly with a {tone} tone, while being mindful of their biases."

        personas.append({
            "name": name,
            "goals": goals,
            "biases": biases,
            "tone": tone,
            "bio": bio.strip(),
            "expected_behavior": behavior.strip()
        })

    return personas
