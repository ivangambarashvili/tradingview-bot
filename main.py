from fastapi import FastAPI, Request
from openai import OpenAI
import os

app = FastAPI()

# Создаём клиент OpenAI с API-ключом из переменной окружения
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/")
def root():
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message", "No message")

    prompt = f"Сигнал: '{message}'. Дай краткий торговый анализ, как трейдер-аналитик."

    # Новый способ вызова чата в openai>=1.0.0
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты опытный криптоаналитик."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content
    return {"response": answer}
