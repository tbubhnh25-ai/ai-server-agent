import subprocess
import sys

from app.config import settings

if sys.platform != "win32":
    import resource

BLOCKED_SUBSTRINGS = [
    "rm -rf /",
    "mkfs",
    ":(){ :|:& };:",
    "> /dev/sda",
    "chmod -R 777 /",
    "dd if=",
]


def is_blocked(command: str) -> str | None:
    lowered = command.lower()
    for pattern in BLOCKED_SUBSTRINGS:
        if pattern in lowered:
            return pattern
    return None


def _limit_resources() -> None:
    mem_bytes = settings.sandbox_memory_limit_mb * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
    resource.setrlimit(resource.RLIMIT_CPU, (settings.shell_timeout_seconds, settings.shell_timeout_seconds))
    resource.setrlimit(resource.RLIMIT_NPROC, (64, 64))


_PREEXEC = _limit_resources if sys.platform != "win32" else None


def run_shell(command: str) -> tuple[bool, str]:
    """
    מריץ פקודת shell בתוך תהליך-בן מוגבל (זמן/זיכרון/מספר תהליכים),
    מוגבל לתיקיית ה-workspace. אין כאן בידוד קונטיינר נפרד (כמו Docker) -
    זה מתאים לפריסה על שירות יחיד כמו Render, שבו השירות עצמו רץ כבר
    בקונטיינר מבודד. לבידוד חזק יותר יש להריץ את הפרויקט בסביבה שמאפשרת
    Docker-in-Docker ולהחזיר את מנגנון ה-sandbox הנפרד.
    """
    blocked = is_blocked(command)
    if blocked:
        return False, f"הפקודה נחסמה (תבנית הרסנית: {blocked})"

    try:
        result = subprocess.run(
            ["/bin/sh", "-c", command],
            cwd=settings.workspace_dir,
            capture_output=True,
            timeout=settings.shell_timeout_seconds,
            preexec_fn=_PREEXEC,
        )
        output = (result.stdout or b"") + (result.stderr or b"")
        return result.returncode == 0, output.decode("utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return False, f"הפקודה חרגה מזמן המקסימום ({settings.shell_timeout_seconds} שניות)"
    except Exception as exc:
        return False, str(exc)
