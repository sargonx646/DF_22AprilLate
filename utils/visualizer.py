import wordcloud
import matplotlib.pyplot as plt
import networkx as nx
import plotly.graph_objects as go
from typing import List, Dict

def generate_visuals(keywords: List[str], transcript: List[Dict]):
    """
    Generate visualizations: a word cloud of key themes and a network graph of stakeholder interactions.

    Args:
        keywords (List[str]): List of extracted keywords.
        transcript (List[Dict]): Debate transcript with agent, round, step, and message.
    """
    try:
        # Generate Word Cloud
        wordcloud_obj = wordcloud.WordCloud(width=800, height=400, background_color='white', max_words=15).generate(' '.join(keywords))
        plt.figure(figsize=(10,
