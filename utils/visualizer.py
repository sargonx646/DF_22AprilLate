import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from typing import List, Dict

def generate_visuals(keywords: List[str], transcript: List[Dict]) -> None:
    """
    Generate visualizations (word cloud and heatmap) from keywords and transcript.

    Args:
        keywords (List[str]): Keywords from summarization.
        transcript (List[Dict]): Debate transcript with agent and message.
    """
    # Word Cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(" ".join(keywords))
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.savefig('visualization.png', bbox_inches='tight')
    plt.close()

    # Heatmap: Analyze main topics per stakeholder
    # Define topics based on extracted issues or keywords
    topics = ["humanitarian", "security", "economic", "political"]  # Example topics
    topic_counts = {agent: {topic: 0 for topic in topics} for agent in set(entry["agent"] for entry in transcript)}
    
    for entry in transcript:
        agent = entry["agent"]
        message = entry["message"].lower()
        # Count topic mentions
        for topic in topics:
            if topic in message:
                topic_counts[agent][topic] += message.count(topic)
    
    # Convert to DataFrame
    df = pd.DataFrame.from_dict(topic_counts, orient='index')
    
    # Generate Heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(df, annot=True, cmap="YlGnBu", fmt="d")
    plt.title("Stakeholder Topic Focus Heatmap")
    plt.xlabel("Topics")
    plt.ylabel("Stakeholders")
    plt.savefig('heatmap.png', bbox_inches='tight')
    plt.close()
