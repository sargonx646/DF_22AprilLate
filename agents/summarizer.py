import json
import os
from openai import OpenAI
from typing import List, Dict, Tuple
from config import MAX_TOKENS, TIMEOUT_S

def summarize_and_analyze(transcript: List[Dict]) -> Tuple[str, List[str], str]:
    """
    Analyze the debate transcript to provide a detailed summary, extract keywords, and suggest optimizations using xAI's Grok-3-Mini-Beta.

    Args:
        transcript (List[Dict]): Debate transcript with agent and message.

    Returns:
        Tuple[str, List[str], str]: Summary, keywords, and optimization suggestion.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    prompt = (
        "You are Grok-3-Mini-Beta, an AI specializing in deep analysis of decision-making debates. Given a debate transcript, provide:\n"
        "1. **Summary** (150–200 words): A concise overview of the debate, highlighting key arguments, stakeholder positions, and outcomes.\n"
        "2. **Keywords** (8–12): Thematic keywords reflecting core issues and dynamics (e.g., 'humanitarian aid', 'security').\n"
        "3. **Suggestion** (100–150 words): Actionable recommendations to improve decision-making, addressing:\n"
        "   - **Faultlines**: Conflicts between stakeholders (e.g., opposing priorities).\n"
        "   - **Chokepoints**: Process steps or dynamics slowing progress (e.g., budget constraints).\n"
        "   - **Contentious Issues**: Topics sparking debate (e.g., resource allocation).\n"
        "   - **Improvements**: Specific changes to stakeholder roles, process steps, or mitigation of biases.\n"
        "Return a JSON object with keys: 'summary' (string), 'keywords' (list of strings), 'suggestion' (string).\n"
        f"Transcript:\n{json.dumps(transcript, indent=2)}\n"
        "Wrap the response in triple backticks (```json\n...\n```)."
    )

    try:
        completion = client.chat.completions.create(
            model="grok-3-mini-beta",
            reasoning_effort="high",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        print(f"Summarization Reasoning: {completion.choices[0].message.reasoning_content}")
        content = completion.choices[0].message.content
        if content.startswith("```json\n") and content.endswith("\n```"):
            content = content[7:-4].strip()
        result = json.loads(content)
        return (
            result.get("summary", "No summary available."),
            result.get("keywords", ["decision", "stakeholder", "debate"]),
            result.get("suggestion", "No suggestion available.")
        )
    except Exception as e:
        print(f"Summarization API Error: {str(e)}")
        return (
            "The debate focused on stakeholder priorities but lacked consensus.",
            ["decision", "stakeholder", "debate"],
            "Encourage structured facilitation to align stakeholders."
        )
