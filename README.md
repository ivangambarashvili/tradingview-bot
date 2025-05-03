# TradingView Bot - AI Signal System

## 🚀 Overview
Проект состоит из двух отдельных компонентов, развёрнутых через Render:

### 1. FastAPI Backend (Webhook API)
- ✉️ URL: https://tradingview-bot-lmod.onrender.com
- 🔢 Файл: `main.py`
- 🛠️ Описание:
  - Обрабатывает POST-запросы на `/webhook`
  - Вызывает OpenAI API (ChatGPT), чтобы дать краткий AI-анализ сигнала
  - Возвращает ответ с анализом в формате JSON

### 2. Streamlit Интерфейс
- 📈 URL: https://tradingview-bot-1.onrender.com
- 🔢 Файл: `app.py`
- 🛠️ Описание:
  - Отображает таблицу сигналов из файла `signals_ready.json`
  - Интерфейс обновляется каждые 5 минут (можно вручную)
  - Планируется добавить фильтры, кнопки, ручной вход в сделки

---

## 🌐 Deployment
### Backend (FastAPI):
- Размещён через Render Web Service
- Используется `uvicorn` для запуска сервера
- Требуется файл `requirements.txt` с зависимостями:
```
fastapi
uvicorn
openai
```

### Frontend (Streamlit):
- Размещён также через Render (отдельный сервис)
- Использует `streamlit`, `pandas`, `json`

---

## 🔍 Текущий прогресс
- ✅ Интерфейс подключён и отображает таблицу сигналов
- ✅ Webhook успешно принимает POST-запросы и отвечает AI-анализом
- ✅ Работа с WebSocket и TA-индикаторами — в процессе (локально)

---

## 🚧 TODO
- [ ] Подключить автоматическую отправку сигналов в `/webhook`
- [ ] Вынести WebSocket бот в облако (Railway/VPS)
- [ ] Расширить Streamlit-интерфейс: фильтры, конфигурации, комментарии
- [ ] Добавить логирование событий и PnL статистику

