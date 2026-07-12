import asyncio
import json
from datetime import datetime

import main


class DummyRequest:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    async def json(self):
        if self.error is not None:
            raise self.error
        return self.payload


class FixedDatetime(datetime):
    @classmethod
    def utcnow(cls):
        return cls(2025, 5, 3, 12, 30)


def test_root_reports_running_status():
    assert main.root() == {"status": "Bot is running"}


def test_webhook_creates_signal_file(monkeypatch, tmp_path):
    signals_file = tmp_path / "signals.json"
    payload = {"symbol": "BTCUSDT", "side": "BUY"}
    monkeypatch.setattr(main, "SIGNALS_FILE", str(signals_file))
    monkeypatch.setattr(main, "datetime", FixedDatetime)

    response = asyncio.run(main.webhook(DummyRequest(payload=payload)))

    assert response == {"response": "Signal saved successfully ✅"}
    assert json.loads(signals_file.read_text()) == [
        {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "received_at": "2025-05-03T12:30:00",
        }
    ]


def test_webhook_prepends_signal_and_limits_history(monkeypatch, tmp_path):
    signals_file = tmp_path / "signals.json"
    signals_file.write_text(json.dumps([{"id": index} for index in range(105)]))
    monkeypatch.setattr(main, "SIGNALS_FILE", str(signals_file))
    monkeypatch.setattr(main, "datetime", FixedDatetime)

    asyncio.run(main.webhook(DummyRequest(payload={"id": "new"})))

    saved_signals = json.loads(signals_file.read_text())
    assert len(saved_signals) == 100
    assert saved_signals[0] == {
        "id": "new",
        "received_at": "2025-05-03T12:30:00",
    }
    assert saved_signals[-1] == {"id": 98}


def test_webhook_returns_500_for_invalid_payload():
    response = asyncio.run(
        main.webhook(DummyRequest(error=ValueError("invalid payload")))
    )

    assert response.status_code == 500
    assert json.loads(response.body) == {"error": "invalid payload"}
