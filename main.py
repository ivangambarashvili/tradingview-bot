from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
import os
from datetime import datetime

app = FastAPI()

SIGNALS_FILE = "signals_ready.json"

@app.get("/")
def root():
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()

        # Загружаем существующие сигналы
        if os.path.exists(SIGNALS_FILE):
            with open(SIGNALS_FILE, "r") as f:
                signals = json.load(f)
        else:
            signals = []

        # Добавляем временную метку, если нет
        data["received_at"] = datetime.utcnow().isoformat()

        # Добавляем сигнал в начало списка
        signals.insert(0, data)

        # Ограничиваем размер истории (например, 100 сигналов)
        signals = signals[:100]

        # Сохраняем файл
        with open(SIGNALS_FILE, "w") as f:
            json.dump(signals, f, indent=2)

        return {"response": "Signal saved successfully ✅"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
