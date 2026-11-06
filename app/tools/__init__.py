from app.tools.fs_tools import fs_read, fs_write
from app.tools.http_fetch import http_fetch
from app.tools.package_install import package_install
from app.tools.shell_exec import shell_exec
from app.tools.web_search import web_search

TOOLS = {
    "shell_exec": lambda args: shell_exec(args["command"]),
    "fs_read": lambda args: fs_read(args["path"]),
    "fs_write": lambda args: fs_write(args["path"], args["content"]),
    "http_fetch": lambda args: http_fetch(args["url"]),
    "web_search": lambda args: web_search(args["query"]),
    "package_install": lambda args: package_install(args["manager"], args["package"]),
}

TOOL_DESCRIPTIONS = """
כלים זמינים:
- shell_exec(command): הרצת פקודת shell בתוך sandbox מבודד
- fs_read(path): קריאת קובץ מתיקיית ה-workspace
- fs_write(path, content): כתיבת קובץ לתיקיית ה-workspace
- http_fetch(url): הבאת תוכן עמוד אינטרנט (http/https ציבורי בלבד)
- web_search(query): חיפוש חינמי ברשת (DuckDuckGo)
- package_install(manager, package): התקנת חבילה (apt-get/pip/npm)
"""
