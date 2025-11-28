"""Configuration for Grammar Engine"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Paths
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = DATA_DIR / "models"
TEST_CASES_DIR = DATA_DIR / "test_cases"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
TEST_CASES_DIR.mkdir(exist_ok=True)

# Performance targets
TARGET_LATENCY_MS = 100
TARGET_ACCURACY_PCT = 85

# FastAPI
API_HOST = "0.0.0.0"
API_PORT = 8000
API_LOG_LEVEL = "info"

# Language Tool settings
LANGUAGE_TOOL_CONFIG = {
    'enabled_rules': ['GRAMMAR', 'SPELL', 'STYLE'],
    'language': 'en-US',
}

# Model settings
SPACY_MODEL = "en_core_web_sm"
NLTK_RESOURCES = ['averaged_perceptron_tagger', 'punkt', 'wordnet']

# Logging
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "grammar_engine.log"

# Debug mode
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
