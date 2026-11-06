import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings


def log_event(task_id: str, event_type: str, data: dict) -> None:
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "task_id": task_id,
        "type": event_type,
        **data,
    }
    path = Path(settings.audit_log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
