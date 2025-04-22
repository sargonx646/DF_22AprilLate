import json
from openai import OpenAI
from typing import List, Dict, Tuple
from config import MAX_TOKENS, TIMEOUT_S

def summarize_and_analyze(transcript: List[Dict]) -> Tuple[str, List[str], str]:
    """
    Summarize the debate transcript, extract keywords, and provide an optimization suggestion using xAI's Grok-3-Mini-Beta.

    Args:
        transcript (List[Dict]): Debate transcript with agent and message.

    Returns:
        Tuple[str, List[str], str]: Summary, keywords, and optimization suggestion.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key="xai-RXSTGBf9LckPtkQ6aBySC0LmpdIjqq9fSSK49PcdRvpLHmldwXEuPwlK9n9AsNfXsHps86amuUFE053u"
    )

    prompt = (
        "You are Grok-3-Mini-Beta, an AI specializing in analyzing debates. Given a debate transcript, provide a concise summary (100-150 words), extract 5-10 key thematic keywords, and suggest one actionable optimization for the decision-making process. Return a JSON object with keys: 'summary' (string), 'keywords' (list of strings), 'suggestion' (string).\n"
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
