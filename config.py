import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "nousresearch/deephermes-3-llama-3-8b-preview:free"
TIMEOUT_S = 15
MAX_RETRIES = 3
RETRY_DELAY = 1

# Application settings
MAX_STAKEHOLDERS = 10  # Increased to support up to 10 stakeholders
MIN_STAKEHOLDERS = 3
DEBATE_ROUNDS = 3

# Decision type categories
DECISION_TYPES = [
    "Budget Allocation",
    "Foreign Policy",
    "Corporate Strategy",
    "Humanitarian Response",
    "Regulatory Compliance",
    "Operational Efficiency",
    "Other"
]

# Psychological traits, influences, biases, and historical behavior options
STAKEHOLDER_ANALYSIS = {
    "psychological_traits": [
        "Risk-Averse",
        "Risk-Tolerant",
        "Collaborative",
        "Authoritative",
        "Empathetic",
        "Analytical",
        "Impulsive"
    ],
    "influences": [
        "Political Pressure",
        "Financial Incentives",
        "Public Opinion",
        "Regulatory Constraints",
        "Strategic Alliances",
        "Personal Ambition"
    ],
    "biases": [
        "Confirmation Bias",
        "Status Quo Bias",
        "Optimism Bias",
        "Cost-Avoidance Bias",
        "Groupthink"
    ],
    "historical_behavior": [
        "Conservative Decision-Making",
        "Innovative Initiatives",
        "Compliance-Driven",
        "Aggressive Expansion",
        "Consensus-Building"
    ]
}
