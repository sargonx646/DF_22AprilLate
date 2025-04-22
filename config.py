# Configuration settings for DecisionTwin for Decision Making

# Decision types
DECISION_TYPES = [
    "Strategic",
    "Tactical",
    "Operational",
    "Financial",
    "Policy",
    "Ethical",
    "Crisis",
    "Other"
]

# Stakeholder analysis suggestions
STAKEHOLDER_ANALYSIS = {
    "psychological_traits": [
        "risk-averse",
        "risk-tolerant",
        "collaborative",
        "competitive",
        "analytical",
        "decisive",
        "cautious",
        "impulsive"
    ],
    "influences": [
        "regulatory bodies",
        "public opinion",
        "shareholders",
        "media",
        "competitors",
        "government policies",
        "industry trends"
    ],
    "biases": [
        "confirmation bias",
        "optimism bias",
        "groupthink",
        "status quo bias",
        "cost-avoidance bias",
        "anchoring bias"
    ],
    "historical_behavior": [
        "prioritizes short-term gains",
        "focuses on long-term strategy",
        "consensus-driven",
        "unilateral decision-maker",
        "data-driven",
        "resistant to change"
    ]
}

# Simulation constraints
MIN_STAKEHOLDERS = 4
MAX_STAKEHOLDERS = 10

# Debate simulation settings
DEBATE_ROUNDS = 5
MAX_TOKENS = 4000
TIMEOUT_S = 60
