from app.sandbox.subprocess_runner import run_shell


def shell_exec(command: str) -> tuple[bool, str]:
    return run_shell(command)
