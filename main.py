import hmac
import json
import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

SIGNALS_FILE = "signals_ready.json"
MAX_SIGNALS = 100

# Shared secret used to authenticate incoming webhook requests.
# Must be provided via the environment; the endpoint is disabled if unset.
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")


def verify_webhook_token(x_webhook_token: Optional[str] = Header(default=None)) -> None:
    if not WEBHOOK_SECRET:
        # Fail closed: refuse to accept signals when no secret is configured.
        raise HTTPException(status_code=503, detail="Webhook is not configured")
    if not x_webhook_token or not hmac.compare_digest(x_webhook_token, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Unauthorized")


class Signal(BaseModel):
    # Reject unknown fields so arbitrary attacker-controlled data can't be stored.
    model_config = {"extra": "forbid"}

    symbol: str = Field(min_length=1, max_length=32)
    side: str = Field(min_length=1, max_length=16)
    reason: str = Field(default="", max_length=1000)
    confidence: str = Field(default="", max_length=64)
    comment: str = Field(default="", max_length=1000)
    timestamp: str = Field(default="", max_length=64)


@app.get("/")
def root():
    return {"status": "Bot is running"}


@app.post("/webhook")
async def webhook(signal: Signal, _: None = Depends(verify_webhook_token)):
    try:
        if os.path.exists(SIGNALS_FILE):
            with open(SIGNALS_FILE, "r", encoding="utf-8") as f:
                signals = json.load(f)
            if not isinstance(signals, list):
                signals = []
        else:
            signals = []

        record = signal.model_dump()
        record["received_at"] = datetime.now(timezone.utc).isoformat()

        signals.insert(0, record)
        signals = signals[:MAX_SIGNALS]

        with open(SIGNALS_FILE, "w", encoding="utf-8") as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)

        return {"response": "Signal saved successfully"}

    except Exception:
        # Avoid leaking internal error details to the client.
        return JSONResponse(status_code=500, content={"error": "Internal server error"})
