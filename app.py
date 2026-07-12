import streamlit as st
import json
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="AI Сигналы", layout="wide")

# ===== Настройки автообновления =====
st_autorefresh(interval=300000, key="refresh")  # каждые 5 мин

st.title("🤖 Сигналы от ChatGPT для Binance Futures")

# ===== Загрузка сигналов =====
def load_signals(path="signals_ready.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

signals = load_signals()

# ===== Фильтры =====
symbols = sorted(list(set([s["symbol"] for s in signals])))
selected_symbol = st.selectbox("Фильтр по паре:", ["Все"] + symbols)
confidence_levels = ["Все", "Высокая", "Средняя", "Низкая"]
selected_confidence = st.selectbox("Фильтр по уверенности:", confidence_levels)

# ===== Преобразование в DataFrame =====
def format_signal(sig):
    return {
        "Пара": sig["symbol"],
        "Сигнал": sig["side"],
        "Причина": sig["reason"],
        "Уверенность": sig["confidence"],
        "Комментарий": sig.get("comment", "—"),
        "Время": sig.get("timestamp", "")
    }

rows = [format_signal(s) for s in signals]
df = pd.DataFrame(rows)

# ===== Применение фильтров =====
if selected_symbol != "Все":
    df = df[df["Пара"] == selected_symbol]

if selected_confidence != "Все":
    df = df[df["Уверенность"] == selected_confidence]

# ===== Отображение =====
st.dataframe(df, use_container_width=True)

st.markdown("---")
st.caption("Streamlit терминал сигналов от ChatGPT • v1.0")
