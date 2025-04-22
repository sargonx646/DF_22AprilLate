import wordcloud
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
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
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud_obj, interpolation='bilinear')
        plt.axis('off')
        plt.savefig('visualization.png', bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Word Cloud Generation Error: {str(e)}")

    try:
        # Generate Network Graph of Stakeholder Interactions
        G = nx.Graph()
        stakeholders = list(set(entry["agent"] for entry in transcript))

        # Add nodes (stakeholders)
        for stakeholder in stakeholders:
            G.add_node(stakeholder)

        # Add edges based on mentions in the transcript
        for entry in transcript:
            speaker = entry["agent"]
            message = entry["message"].lower()
            for other_stakeholder in stakeholders:
                if other_stakeholder != speaker and other_stakeholder.lower() in message:
                    if G.has_edge(speaker, other_stakeholder):
                        G[speaker][other_stakeholder]["weight"] += 1
                    else:
                        G.add_edge(speaker, other_stakeholder, weight=1)

        # Create positions for nodes using a spring layout
        pos = nx.spring_layout(G)

        # Extract edge weights for visualization
        edge_x = []
        edge_y = []
        edge_weights = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.append(edge[2]["weight"])

        # Create edge trace with weighted lines
        edge_trace = go.Scatter(
            x=edge_x,
            y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Create node trace with labels
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=list(G.nodes()),
            textposition="top center",
            hoverinfo='text',
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=15,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                )
            )
        )

        # Color nodes by the number of connections
        node_adjacencies = [len(list(G.neighbors(node))) for node in G.nodes()]
        node_trace.marker.color = node_adjacencies

        # Create the figure
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Stakeholder Interaction Network',
                            titlefont_size=16,
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            annotations=[dict(
                                text="Interactions based on mentions in the debate",
                                showarrow=False,
                                xref="paper", yref="paper",
                                x=0.005, y=-0.002)],
                            xaxis=dict(showgrid=False, zeroline=False),
                            yaxis=dict(showgrid=False, zeroline=False))
                        )

        # Save the figure as an HTML file
        fig.write_html("network_graph.html")
    except Exception as e:
        print(f"Network Graph Generation Error: {str(e)}")
