import json
import os
from openai import OpenAI
from typing import List, Dict, Tuple

def summarize_and_analyze(transcript: List[Dict]) -> Tuple[str, List[str], str]:
    """
    Summarize the debate, extract keywords, identify faultlines, chokepoints, and provide optimization suggestions.

    Args:
        transcript (List[Dict]): Debate transcript with agent, round, step, and message.

    Returns:
        Tuple[str, List[str], str]: Summary, keywords, and optimization suggestion.
    """
    client = OpenAI(
        base_url="https://api.x.ai/v1",
        api_key=os.getenv("XAI_API_KEY")
    )

    transcript_json = json.dumps(transcript, indent=2)

    prompt = (
        "You are an AI assistant analyzing a decision-making debate transcript for DecisionTwin. Your task is to:\n"
        "1. Summarize the debate in 150–200 words, capturing key arguments, decisions, and outcomes across all rounds.\n"
        "2. Extract 10–15 keywords that represent the main themes (e.g., humanitarian, security, budget).\n"
        "3. Identify faultlines (major conflicts or disagreements between stakeholders, e.g., humanitarian focus vs. security priorities).\n"
        "4. Identify chokepoints (process bottlenecks or constraints, e.g., budget limitations, lack of consensus).\n"
        "5. Provide actionable recommendations (150–200 words) to optimize the decision-making process, such as role adjustments, process changes, or mitigation strategies for faultlines and chokepoints. Include specific steps to improve stakeholder collaboration and decision outcomes.\n"
        "Return the results in JSON format with fields 'summary', 'keywords', 'faultlines', 'chokepoints', and 'suggestion'.\n"
        f"Transcript:\n{transcript_json}\n"
    )

    try:
        completion = client.chat.completions.create(
            model="grok-3-beta",
            messages=[
                {"role": "system", "content": "You are an AI assistant analyzing debate transcripts."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        result = json.loads(completion.choices[0].message.content)
        summary = result.get("summary", "No summary generated.")
        keywords = result.get("keywords", [])
        faultlines = result.get("faultlines", "No faultlines identified.")
        chokepoints = result.get("chokepoints", "No chokepoints identified.")
        suggestion = result.get("suggestion", "No suggestions provided.")

        # Combine faultlines and chokepoints into the suggestion for display
        enhanced_suggestion = f"Faultlines: {faultlines}\nChokepoints: {chokepoints}\nRecommendations: {suggestion}"
        return summary, keywords, enhanced_suggestion

    except Exception as e:
        print(f"Summarization Error: {str(e)}")
        summary = "The debate focused on key decision points, but a detailed summary could not be generated due to an error."
        keywords = ["decision", "stakeholders", "process", "debate"]
        suggestion = "Consider reviewing the process steps and stakeholder roles to ensure alignment and clarity."
        return summary, keywords, suggestion
