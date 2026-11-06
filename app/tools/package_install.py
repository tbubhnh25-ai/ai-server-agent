from app.sandbox.subprocess_runner import run_shell

# apt-get הוסר: בלי קונטיינר sandbox נפרד, פקודה זו תרוץ בתוך תהליך השירות עצמו
# (דורש הרשאות root שלרוב אין לו ב-Render, ומשנה את הסביבה הפעילה עצמה).
ALLOWED_MANAGERS = {"pip", "pip3", "npm"}


def package_install(manager: str, package: str) -> tuple[bool, str]:
    if manager not in ALLOWED_MANAGERS:
        return False, f"מנהל חבילות '{manager}' לא מאושר"

    commands = {
        "pip": f"pip install --no-cache-dir {package}",
        "pip3": f"pip3 install --no-cache-dir {package}",
        "npm": f"npm install -g {package}",
    }
    return run_shell(commands[manager])
