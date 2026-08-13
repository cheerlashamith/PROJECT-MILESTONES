"""
Central Configuration for Agentic AI for Safety Monitoring with Construction Risk Analytics
========================================================
All tuneable parameters in one place. Swap models, adjust prompts,
or change timeouts without touching any other file.
"""

import os
from dataclasses import dataclass, field

# Load .env manually to avoid requiring python-dotenv
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(env_path):
    with open(env_path) as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ[k] = v


@dataclass
class Config:
    """Central configuration for the CIH application."""

    # ── OpenAI / Model Settings ──────────────────────────────────────
    MODEL_NAME: str = "gpt-4o-mini"
    OLLAMA_HOST: str = "https://api.openai.com"
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 2048
    TIMEOUT: int = 600  # seconds

    # ── Supported Models (for UI dropdown / fallback) ────────────────
    SUPPORTED_MODELS: list = field(default_factory=lambda: [
        "llama3.1",
        "qwen3:14b",
        "gemma3:4b",
        "qwen2.5:7b",
    ])

    # ── System Prompt ────────────────────────────────────────────────
    SYSTEM_PROMPT: str = (
        "You are ACRA-AI, the AI assistant for the Agentic AI for Safety Monitoring with Construction Risk Analytics project.\n\n"
        "You are ONLY allowed to answer questions related to:\n"
        "- Civil Engineering\n"
        "- Construction\n"
        "- House Planning\n"
        "- Material Estimation\n"
        "- Cost Estimation\n"
        "- RCC Structures\n"
        "- Steel, Cement, Sand, Bricks, Concrete\n"
        "- Plumbing & Electrical\n"
        "- Construction Management & Safety\n"
        "- Building Regulations\n"
        "- Agentic AI for Safety Monitoring with Construction Risk Analytics Project\n\n"
        "If the question is unrelated to construction (e.g., sports, movies, politics, celebrities, medicine, finance, general knowledge), YOU MUST REFUSE TO ANSWER.\n"
        "Reply EXACTLY with:\n"
        "\"I'm designed specifically for the Agentic AI for Safety Monitoring with Construction Risk Analytics project. I cannot answer questions about sports, movies, politics, celebrities, medicine, finance, or general knowledge. Please ask a construction-related question.\"\n\n"
        "If the user asks to build or generate a 3D model based on measurements, you MUST output a valid JSON block enclosed in `<3D_MODEL>` and `</3D_MODEL>` tags. "
        "The JSON must have a 'rooms' array, where each room has 'name', 'width', 'length', 'x', 'z', and 'color' (hex code). "
        "Always explain calculations and provide practical, accurate advice for valid construction queries."
    )

    # ── Logging ──────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "logs",
    )

    # ── Memory / Conversation ────────────────────────────────────────
    MAX_CONVERSATION_MESSAGES: int = 20  # sliding window size

    # ── Material Pricing (USD per unit) ──────────────────────────────
    MATERIAL_PRICES: dict = field(default_factory=lambda: {
        "Cement":    {"price": 8.00,   "unit": "bag"},
        "Sand":      {"price": 25.00,  "unit": "ton"},
        "Bricks":    {"price": 0.50,   "unit": "piece"},
        "Steel":     {"price": 800.00, "unit": "ton"},
        "Aggregate": {"price": 30.00,  "unit": "ton"},
        "Tiles":     {"price": 3.50,   "unit": "sq ft"},
        "Paint":     {"price": 12.00,  "unit": "liter"},
    })

    # ── House Type Multipliers ───────────────────────────────────────
    HOUSE_TYPE_MULTIPLIERS: dict = field(default_factory=lambda: {
        "Single Story": 1.0,
        "Double Story":  1.05,
        "Villa":         1.20,
        "Apartment":     0.90,
        "Commercial":    1.40,
    })
