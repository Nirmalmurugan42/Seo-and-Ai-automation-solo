"""
Central configuration for the SEO Intelligence Agent.

All secrets are read from environment variables (.env file).
Nothing sensitive is hard-coded.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Your site
# ---------------------------------------------------------------------------
OWN_DOMAIN = os.getenv("OWN_DOMAIN", "jypragroup.com.au")
OWN_BRAND = os.getenv("OWN_BRAND", "Jypra Group")

# ---------------------------------------------------------------------------
# SerpAPI
# ---------------------------------------------------------------------------
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
SERP_LOCATION = os.getenv("SERP_LOCATION", "Brisbane, Queensland, Australia")
SERP_GL = os.getenv("SERP_GL", "au")
SERP_HL = os.getenv("SERP_HL", "en")
SERP_NUM = int(os.getenv("SERP_NUM", "10"))

# ---------------------------------------------------------------------------
# LLM Provider
# Choose ONE: replicate | anthropic | openai | ollama
# ---------------------------------------------------------------------------
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower().strip()

# Ollama local free model
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Replicate
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN", "")
REPLICATE_MODEL = os.getenv(
    "REPLICATE_MODEL",
    "meta/meta-llama-3.1-70b-instruct",
)

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# ---------------------------------------------------------------------------
# Run controls
# ---------------------------------------------------------------------------
MAX_KEYWORDS = int(os.getenv("MAX_KEYWORDS", "10"))

TARGET_GROUPS = [
    "Quick Win",
    "Local SEO",
    "Commercial",
    "Gap Opportunity",
]

COMPETITORS_PER_KEYWORD = int(os.getenv("COMPETITORS_PER_KEYWORD", "3"))

REQUEST_TIMEOUT = 20

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)