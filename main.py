import json
import logging
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request

app = FastAPI()
logger = logging.getLogger(__name__)

SIGNALS_FILE = "signals_ready.json"


def load_signals():
    try:
        with open(SIGNALS_FILE, "r", encoding="utf-8") as file:
            signals = json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as exc:
        logger.exception("Signal history contains invalid JSON")
        raise HTTPException(
            status_code=500,
            detail="Signal history is unavailable",
        ) from exc
    except OSError as exc:
        logger.exception("Failed to read signal history")
        raise HTTPException(
            status_code=500,
            detail="Signal history is unavailable",
        ) from exc

    if not isinstance(signals, list):
        logger.error("Signal history must contain a JSON array")
        raise HTTPException(
            status_code=500,
            detail="Signal history is unavailable",
        )

    return signals


def save_signals(signals):
    try:
        with open(SIGNALS_FILE, "w", encoding="utf-8") as file:
            json.dump(signals, file, indent=2, ensure_ascii=False)
    except OSError as exc:
        logger.exception("Failed to write signal history")
        raise HTTPException(
            status_code=500,
            detail="Signal could not be saved",
        ) from exc


@app.get("/")
def root():
    return {"status": "Bot is running"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("Rejected webhook with invalid JSON: %s", exc)
        raise HTTPException(
            status_code=400,
            detail="Request body must contain valid JSON",
        ) from exc

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=422,
            detail="Request body must be a JSON object",
        )

    signals = load_signals()
    data["received_at"] = datetime.utcnow().isoformat()
    signals.insert(0, data)
    save_signals(signals[:100])

    return {"response": "Signal saved successfully ✅"}
