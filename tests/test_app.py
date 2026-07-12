import importlib
import json
import sys
from types import ModuleType


class FakeStreamlit(ModuleType):
    def __init__(self, selections):
        super().__init__("streamlit")
        self.selections = iter(selections)
        self.dataframes = []

    def set_page_config(self, **config):
        self.page_config = config

    def title(self, text):
        self.title_text = text

    def selectbox(self, label, options):
        return next(self.selections)

    def dataframe(self, dataframe, use_container_width):
        self.dataframes.append((dataframe.copy(), use_container_width))

    def markdown(self, text):
        self.markdown_text = text

    def caption(self, text):
        self.caption_text = text


def load_app(monkeypatch, tmp_path, selections=("Все", "Все"), signals=None):
    if signals is not None:
        (tmp_path / "signals_ready.json").write_text(
            json.dumps(signals), encoding="utf-8"
        )

    fake_streamlit = FakeStreamlit(selections)
    fake_autorefresh = ModuleType("streamlit_autorefresh")
    fake_autorefresh.st_autorefresh = lambda **settings: settings
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(sys.modules, "streamlit", fake_streamlit)
    monkeypatch.setitem(sys.modules, "streamlit_autorefresh", fake_autorefresh)
    sys.modules.pop("app", None)

    return importlib.import_module("app"), fake_streamlit


def test_app_handles_missing_signals_file(monkeypatch, tmp_path):
    module, fake_streamlit = load_app(monkeypatch, tmp_path)

    assert module.signals == []
    assert module.df.empty
    assert fake_streamlit.page_config == {
        "page_title": "AI Сигналы",
        "layout": "wide",
    }
    assert fake_streamlit.dataframes[0][1] is True


def test_load_signals_and_format_signal(monkeypatch, tmp_path):
    module, _ = load_app(monkeypatch, tmp_path)
    signals_file = tmp_path / "custom_signals.json"
    signal = {
        "symbol": "ETHUSDT",
        "side": "SELL",
        "reason": "RSI is overbought",
        "confidence": "Средняя",
    }
    signals_file.write_text(json.dumps([signal]), encoding="utf-8")

    assert module.load_signals(signals_file) == [signal]
    assert module.load_signals(tmp_path / "missing.json") == []
    assert module.format_signal(signal) == {
        "Пара": "ETHUSDT",
        "Сигнал": "SELL",
        "Причина": "RSI is overbought",
        "Уверенность": "Средняя",
        "Комментарий": "—",
        "Время": "",
    }


def test_app_filters_signals_by_symbol_and_confidence(monkeypatch, tmp_path):
    signals = [
        {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "reason": "Breakout",
            "confidence": "Высокая",
            "comment": "Momentum confirmed",
            "timestamp": "2025-05-03 12:00",
        },
        {
            "symbol": "BTCUSDT",
            "side": "SELL",
            "reason": "Resistance",
            "confidence": "Низкая",
        },
        {
            "symbol": "ETHUSDT",
            "side": "BUY",
            "reason": "Support",
            "confidence": "Высокая",
        },
    ]

    module, fake_streamlit = load_app(
        monkeypatch,
        tmp_path,
        selections=("BTCUSDT", "Высокая"),
        signals=signals,
    )

    assert module.df.to_dict("records") == [
        {
            "Пара": "BTCUSDT",
            "Сигнал": "BUY",
            "Причина": "Breakout",
            "Уверенность": "Высокая",
            "Комментарий": "Momentum confirmed",
            "Время": "2025-05-03 12:00",
        }
    ]
    assert fake_streamlit.dataframes[0][0].equals(module.df)
