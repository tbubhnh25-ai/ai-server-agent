import json
from pathlib import Path

from app.config import settings

_STORE_PATH = Path(settings.workspace_dir) / "runtime_settings.json"
_OVERRIDABLE_KEYS = {"llm_api_key", "llm_provider", "llm_model"}

_cache: dict | None = None


def _load() -> dict:
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(_STORE_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _cache = {}
    return _cache


def get(key: str) -> str:
    override = _load().get(key)
    return override if override else getattr(settings, key)


def set_values(values: dict) -> None:
    data = _load()
    data.update({k: v for k, v in values.items() if k in _OVERRIDABLE_KEYS and v})
    _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    _STORE_PATH.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    global _cache
    _cache = data
