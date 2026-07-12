from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from datetime import datetime

from signal_store import MAX_SIGNALS, load_signals, save_signals

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()

        # Загружаем существующие сигналы
        signals = load_signals()

        # Добавляем временную метку, если нет
        data["received_at"] = datetime.utcnow().isoformat()

        # Добавляем сигнал в начало списка
        signals.insert(0, data)

        # Ограничиваем размер истории (например, 100 сигналов)
        signals = signals[:MAX_SIGNALS]

        # Сохраняем файл
        save_signals(signals)

        return {"response": "Signal saved successfully ✅"}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
