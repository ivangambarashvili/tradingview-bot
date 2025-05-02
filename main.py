from fastapi import FastAPI, Request
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.get("/")
def root():
    return {"status": "Bot is running"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    message = data.get("message", "No message")

    prompt = f"Сигнал: '{message}'. Дай краткий торговый анализ, как трейдер-аналитик."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Ты опытный криптоаналитик."},
            {"role": "user", "content": prompt}
        ]
    )

    answer = response["choices"][0]["message"]["content"]
    return {"response": answer}
