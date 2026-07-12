import json
import os

SIGNALS_FILE = "signals_ready.json"
MAX_SIGNALS = 100


def load_signals(path=SIGNALS_FILE):
    """Load signals from the JSON store, returning [] if missing or unreadable."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_signals(signals, path=SIGNALS_FILE):
    """Persist signals to the JSON store."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(signals, f, indent=2)
