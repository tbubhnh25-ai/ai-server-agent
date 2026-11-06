import docker
from docker.errors import ContainerError, ImageNotFound

from app.config import settings

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


def run_shell(command: str) -> tuple[bool, str]:
    blocked = is_blocked(command)
    if blocked:
        return False, f"הפקודה נחסמה (תבנית הרסנית: {blocked})"

    client = docker.from_env()
    try:
        output = client.containers.run(
            settings.sandbox_image,
            ["/bin/sh", "-c", command],
            remove=True,
            network_mode="bridge",
            mem_limit=settings.sandbox_memory_limit,
            nano_cpus=int(settings.sandbox_cpu_limit * 1_000_000_000),
            volumes={settings.workspace_dir: {"bind": "/workspace", "mode": "rw"}},
            working_dir="/workspace",
            user="agent",
            stderr=True,
            stdout=True,
            timeout=settings.shell_timeout_seconds,
        )
        return True, output.decode("utf-8", errors="replace")
    except ImageNotFound:
        return False, f"תמונת ה-sandbox '{settings.sandbox_image}' לא נמצאה - יש לבנות אותה קודם"
    except ContainerError as exc:
        return False, exc.stderr.decode("utf-8", errors="replace") if exc.stderr else str(exc)
    except Exception as exc:  # docker timeouts and other runtime errors
        return False, str(exc)
