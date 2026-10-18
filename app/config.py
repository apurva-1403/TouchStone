"""Runtime configuration, read from environment variables (and a local .env in development)."""
import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "groovy-analyst-509819-d5")
# Vertex AI location for Gemini calls. "global" has the widest model availability.
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "global")

# Main reasoning / agent model.
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-3.8-flash")
# Hedging: if a call to AGENT_MODEL hasn't answered after HEDGE_AFTER_S, the same call also goes to FALLBACK_MODEL
# and the first answer wins (the rest of that question then stays on the winner). Measured 2026-10-08:
# gemini-3.8-flash calls ranged 2-97 s; gemini-2.5-flash ~1-12 s. Set FALLBACK_MODEL="" to disable.
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gemini-2.5-flash")
HEDGE_AFTER_S = float(os.getenv("HEDGE_AFTER_S", "8"))
# Cheap, fast model for side tasks (query rewriting, classification).
FAST_MODEL = os.getenv("FAST_MODEL", "gemini-3.5-flash-lite")
# Thinking depth for the agent: MINIMAL | LOW | MEDIUM | HIGH. Lower is faster.
AGENT_THINKING = os.getenv("AGENT_THINKING", "LOW")
# Same idea for Gemini 2.x models, which take a token budget instead of a level (0 = no thinking).
AGENT_THINKING_BUDGET = int(os.getenv("AGENT_THINKING_BUDGET", "512"))
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-2")
# Embeddings are truncated to this many dimensions (Matryoshka) and re-normalised.
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", ROOT / "data"))
INDEX_DIR = Path(os.getenv("INDEX_DIR", ROOT / "index"))

# The dataset's simulated "today"; all age calculations are relative to this.
TODAY = date.fromisoformat(os.getenv("SIMULATED_TODAY", "2026-09-24"))
