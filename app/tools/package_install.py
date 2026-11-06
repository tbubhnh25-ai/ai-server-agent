from app.sandbox.docker_runner import run_shell

ALLOWED_MANAGERS = {"apt-get", "pip", "pip3", "npm"}


def package_install(manager: str, package: str) -> tuple[bool, str]:
    if manager not in ALLOWED_MANAGERS:
        return False, f"מנהל חבילות '{manager}' לא מאושר"

    commands = {
        "apt-get": f"apt-get update && apt-get install -y {package}",
        "pip": f"pip install --no-cache-dir {package}",
        "pip3": f"pip3 install --no-cache-dir {package}",
        "npm": f"npm install -g {package}",
    }
    return run_shell(commands[manager])
