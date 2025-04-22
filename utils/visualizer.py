import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd

def generate_visuals(keywords: list[str], transcript: list[dict], wordcloud_path: str = "visualization.png", heatmap_path: str = "heatmap.png") -> None:
    """Generate word cloud and heatmap visualizations for simulation results.

    Args:
        keywords (list[str]): Keywords from summarizer.
        transcript (list[dict]): Debate transcript.
        wordcloud_path (str): Path to save word cloud.
        heatmap_path (str): Path to save heatmap.
    """
    # Word Cloud
    if keywords:
        text = " ".join(keywords)
        wc = WordCloud(
            width=800,
            height=400,
            background_color="white",
            colormap="viridis",
            max_words=10
        ).generate(text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(wordcloud_path, format='png', dpi=300)
        plt.close()

    # Heatmap (agent activity)
    if transcript:
        agents = [entry["agent"] for entry in transcript]
        df = pd.DataFrame({"Agent": agents}).value_counts().reset_index(name="Count")
        pivot = df.pivot_table(index="Agent", values="Count", fill_value=0)
        plt.figure(figsize=(8, 6))
        sns.heatmap(pivot, annot=True, cmap="Blues", fmt=".0f")
        plt.title("Stakeholder Activity Heatmap")
        plt.xlabel("Activity Count")
        plt.ylabel("Stakeholder")
        plt.tight_layout()
        plt.savefig(heatmap_path, format='png', dpi=300)
        plt.close()
