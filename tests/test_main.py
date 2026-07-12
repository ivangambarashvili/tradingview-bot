import json
import tempfile
import unittest
from pathlib import Path

from fastapi import HTTPException

import main


class StubRequest:
    def __init__(self, payload=None, error=None):
        self.payload = payload
        self.error = error

    async def json(self):
        if self.error:
            raise self.error
        return self.payload


class WebhookTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.original_signals_file = main.SIGNALS_FILE
        main.SIGNALS_FILE = str(
            Path(self.temp_directory.name) / "signals_ready.json"
        )

    def tearDown(self):
        main.SIGNALS_FILE = self.original_signals_file
        self.temp_directory.cleanup()

    async def test_rejects_invalid_json(self):
        error = json.JSONDecodeError("Invalid JSON", "", 0)

        with self.assertRaises(HTTPException) as context:
            await main.webhook(StubRequest(error=error))

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            "Request body must contain valid JSON",
        )

    async def test_rejects_non_object_payload(self):
        with self.assertRaises(HTTPException) as context:
            await main.webhook(StubRequest(payload=[]))

        self.assertEqual(context.exception.status_code, 422)

    async def test_reports_corrupt_signal_history_without_leaking_details(self):
        Path(main.SIGNALS_FILE).write_text("{invalid", encoding="utf-8")

        with self.assertRaises(HTTPException) as context:
            await main.webhook(StubRequest(payload={"symbol": "BTCUSDT"}))

        self.assertEqual(context.exception.status_code, 500)
        self.assertEqual(context.exception.detail, "Signal history is unavailable")

    async def test_saves_valid_signal(self):
        response = await main.webhook(
            StubRequest(payload={"symbol": "BTCUSDT", "side": "BUY"})
        )

        signals = json.loads(
            Path(main.SIGNALS_FILE).read_text(encoding="utf-8")
        )
        self.assertEqual(response, {"response": "Signal saved successfully ✅"})
        self.assertEqual(signals[0]["symbol"], "BTCUSDT")
        self.assertIn("received_at", signals[0])


if __name__ == "__main__":
    unittest.main()
