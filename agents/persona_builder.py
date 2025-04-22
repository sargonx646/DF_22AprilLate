from typing import List
import random
import os
from openai import OpenAI

def build_personas(names: List[str], dilemma: str, process_hint: str, stakeholders: List[dict] = None) -> List[dict]:
    """
    Build detailed personas for stakeholders, including AI-generated bios and expected negotiation behaviors,
    based on the user-provided case details and extracted stakeholder data.

    Args:
        names (List[str]): List of stakeholder names.
        dilemma (str): The user-provided decision dilemma.
        process_hint (str): The user-provided process and stakeholder details.
        stakeholders (List[dict]): Extracted stakeholders with bio, traits, etc.

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

    # Map extracted stakeholders for reference
    stakeholder_dict = {s["name"]: s for s in stakeholders} if stakeholders else {}

    personas = []
    for name in names:
        # Use extracted stakeholder data if available
        extracted_data = stakeholder_dict.get(name, {})
        goals = random.sample(goals_options, k=2)
        biases = random.sample(biases_options, k=2)
        tone = extracted_data.get("tone", "unknown") if "tone" in extracted_data else random.choice(tones)

        # Use the bio from extracted data as a starting point
        initial_bio = extracted_data.get("bio", f"{name} has a long career in their field, with extensive experience relevant to the decision at hand.")

        # AI-generated Bio and Expected Behavior
        prompt = (
            f"Generate a detailed bio (150–200 words) and expected negotiation behavior (100–150 words) for a stakeholder named {name}. "
            f"The stakeholder is part of a decision-making process described as follows:\n"
            f"Dilemma: {dilemma}\n"
            f"Process and Stakeholder Details: {process_hint}\n"
            f"Initial Bio (use as a starting point): {initial_bio}\n"
            "Infer the stakeholder's role, priorities, career history, personality, and motivations from the provided dilemma and process details. "
            "Incorporate any stakeholder dynamics or conflicts mentioned in the process hint. "
            "For the bio, detail their professional background, key achievements, and personal traits. "
            "For the expected behavior, describe how they’ll negotiate, considering their goals, biases, tone, and the case specifics (e.g., budget constraints, competing priorities). "
            "Return the result as plain text with the bio and behavior separated by '\n\n'."
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
            if "\n\n" in response:
                bio, behavior = response.split("\n\n", 1)
            else:
                bio = response
                behavior = f"During negotiations, {name} will focus on their primary goals, advocating with a {tone} tone, while being mindful of their biases."
        except Exception as e:
            print(f"Error generating profile for {name}: {str(e)}")
            bio = initial_bio
            behavior = f"During negotiations, {name} will focus on their primary goals, advocating with a {tone} tone, while being mindful of their biases."

        personas.append({
            "name": name,
            "goals": goals,
            "biases": biases,
            "tone": tone,
            "bio": bio.strip(),
            "expected_behavior": behavior.strip()
        })

    return personas
