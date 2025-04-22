import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL_NAME = "nousresearch/deephermes-3-llama-3-8b-preview:free"  # High-performance free model
TIMEOUT_S = 15
MAX_RETRIES = 3
RETRY_DELAY = 1

# Application settings
MAX_STAKEHOLDERS = 7
MIN_STAKEHOLDERS = 3
DEBATE_ROUNDS = 3
