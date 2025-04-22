import os
from openai import OpenAI
from typing import List, Dict

def build_personas(stakeholder_names: List[str]) -> List[Dict]:
    """
    Generate detailed personas for stakeholders using xAI's Grok-3-Mini-Beta model.
    
    Args:
        stakeholder_names (List[str]): List of stakeholder names.
    
    Returns:
        List[Dict]: List of personas with name, goals, biases, and tone.
    """
    # Initialize xAI API client
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key="xai-RXSTGBf9LckPtkQ6aBySC0LmpdIjqq9fSSK49PcdRvpLHmldwXEuPwlK9n9AsNfXsHps86amuUFE053u"
    )
    
    personas = []
    for name in stakeholder_names:
        try:
            # Craft prompt for persona generation
            messages = [
                {
                    "role": "system",
                    "content": "You are a highly intelligent AI assistant skilled in creating detailed stakeholder personas for decision-making simulations. Generate a persona with goals, biases, and tone based on the provided stakeholder name."
                },
                {
                    "role": "user",
                    "content": f"Create a persona for a stakeholder named '{name}'. Provide 2-3 goals (specific to their role in a decision-making context), 2-3 biases (cognitive or situational), and a communication tone (e.g., assertive, diplomatic). Return the response in JSON format."
                }
            ]
            
            # Make API call with reasoning enabled
            completion = client.chat.completions.create(
                model="grok-3-mini-beta",
                reasoning_effort="high",
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            persona_data = json.loads(completion.choices[0].message.content)
            
            # Ensure required fields
            persona = {
                "name": name,
                "goals": persona_data.get("goals", ["Influence decision outcome", "Protect personal interests"]),
                "biases": persona_data.get("biases", ["Confirmation bias", "Status quo bias"]),
                "tone": persona_data.get("tone", "diplomatic")
            }
            
            # Log reasoning for debugging
            print(f"Persona Reasoning for {name}: {completion.choices[0].message.reasoning_content}")
            
            personas.append(persona)
            
        except Exception as e:
            print(f"Error generating persona for {name}: {str(e)}")
            # Fallback persona
            personas.append({
                "name": name,
                "goals": ["Influence decision outcome", "Protect personal interests"],
                "biases": ["Confirmation bias", "Status quo bias"],
                "tone": "diplomatic"
            })
    
    return personas
