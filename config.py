# xAI API configuration
API_URL = "https://api.x.ai/v1"
MODEL_NAME = "grok-3-beta"
TIMEOUT_S = 30
MAX_RETRIES = 3
RETRY_DELAY = 2
MAX_TOKENS = 12000  # Increased for 300–400 word responses per stakeholder

# Decision-making configuration
MIN_STAKEHOLDERS = 3
MAX_STAKEHOLDERS = 10
DECISION_TYPES = [
    "Foreign Policy",
    "Corporate Strategy",
    "Community Development",
    "Other"
]
STAKEHOLDER_ANALYSIS = {
    "psychological_traits": [
        "Analytical",
        "Empathetic",
        "Authoritative",
        "Collaborative",
        "Risk-Averse",
        "Risk-Tolerant"
    ],
    "influences": [
        "Strategic Alliances",
        "Public Opinion",
        "Political Pressure",
        "Financial Incentives",
        "Regulatory Constraints",
        "Personal Ambition"
    ],
    "biases": [
        "Confirmation Bias",
        "Optimism Bias",
        "Groupthink",
        "Status Quo Bias",
        "Cost-Avoidance Bias"
    ],
    "historical_behavior": [
        "Consensus-Building",
        "Innovative Initiatives",
        "Conservative Decision-Making",
        "Compliance-Driven",
        "Aggressive Expansion"
    ]
}
DEBATE_ROUNDS = 5
