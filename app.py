import json
import logging

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="AI Сигналы", layout="wide")
logger = logging.getLogger(__name__)

REQUIRED_SIGNAL_FIELDS = ("symbol", "side", "reason", "confidence")


class SignalsLoadError(RuntimeError):
    pass

# ===== Настройки автообновления =====
st_autorefresh(interval=300000, key="refresh")  # каждые 5 мин

st.title("🤖 Сигналы от ChatGPT для Binance Futures")

# ===== Загрузка сигналов =====
def load_signals(path="signals_ready.json"):
    try:
        with open(path, "r", encoding="utf-8") as file:
            signals = json.load(file)
    except FileNotFoundError as exc:
        raise SignalsLoadError(f"Файл {path} не найден") from exc
    except json.JSONDecodeError as exc:
        raise SignalsLoadError(f"Файл {path} содержит некорректный JSON") from exc
    except OSError as exc:
        raise SignalsLoadError(f"Не удалось прочитать файл {path}") from exc

    if not isinstance(signals, list):
        raise SignalsLoadError(f"Файл {path} должен содержать JSON-массив")

    for index, signal in enumerate(signals):
        if not isinstance(signal, dict):
            raise SignalsLoadError(f"Сигнал #{index + 1} должен быть JSON-объектом")

        missing_fields = [
            field for field in REQUIRED_SIGNAL_FIELDS if field not in signal
        ]
        if missing_fields:
            fields = ", ".join(missing_fields)
            raise SignalsLoadError(
                f"В сигнале #{index + 1} отсутствуют поля: {fields}"
            )

    return signals


try:
    signals = load_signals()
except SignalsLoadError as exc:
    logger.exception("Failed to load signals")
    st.error(f"Не удалось загрузить сигналы: {exc}")
    st.stop()

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
