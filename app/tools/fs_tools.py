from pathlib import Path

from app.config import settings

WORKSPACE = Path(settings.workspace_dir)


def _resolve(relative_path: str) -> Path:
    target = (WORKSPACE / relative_path).resolve()
    if WORKSPACE.resolve() not in target.parents and target != WORKSPACE.resolve():
        raise ValueError("גישה מחוץ ל-Workspace אסורה")
    return target


def fs_read(relative_path: str) -> tuple[bool, str]:
    try:
        target = _resolve(relative_path)
        return True, target.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return False, str(exc)


def fs_write(relative_path: str, content: str) -> tuple[bool, str]:
    try:
        target = _resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return True, f"נכתב בהצלחה: {relative_path}"
    except Exception as exc:
        return False, str(exc)
