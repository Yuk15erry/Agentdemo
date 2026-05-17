"""
Global configuration for the Cross-Border Ecommerce AI System.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "demo")
DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# Model settings
DEFAULT_MODEL = "gpt-4o-mini" if LLM_PROVIDER == "openai" else "claude-3-haiku-20240307"
MAX_TOKENS_PER_REQUEST = 4096
TEMPERATURE = 0.7

# RAG Configuration
RAG_INDEX_PATH = os.getenv("RAG_INDEX_PATH", str(PROJECT_ROOT / "data" / "faiss_index"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
RAG_TOP_K = 5

# ERP Integration
ERP_API_ENDPOINT = os.getenv("ERP_API_ENDPOINT", "http://localhost:3001")
ERP_API_KEY = os.getenv("ERP_API_KEY", "")

# Agent-specific settings
COPYWRITER_MAX_REFINEMENT_ROUNDS = 3
MARKET_INSIGHT_MAX_REVIEWS = 500
CS_MAX_HISTORY_LENGTH = 20

# Supported languages
SUPPORTED_LANGUAGES = ["en", "zh", "th", "id", "vi", "ja", "ko", "es", "ar"]

# Token monitoring
TOKEN_ALERT_THRESHOLD_DAILY = 10_000_000  # 10M tokens

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
