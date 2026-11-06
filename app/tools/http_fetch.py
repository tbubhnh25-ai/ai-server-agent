import ipaddress
import socket
from urllib.parse import urlparse

import httpx

BLOCKED_HOSTNAMES = {"localhost", "metadata.google.internal"}


def _is_private(host: str) -> bool:
    try:
        addr = ipaddress.ip_address(socket.gethostbyname(host))
        return addr.is_private or addr.is_loopback or addr.is_link_local
    except (socket.gaierror, ValueError):
        return True  # לא ניתן לפענח - נחסם לפי כלל "safe by default"


def http_fetch(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, "רק כתובות http/https מותרות"
    if parsed.hostname in BLOCKED_HOSTNAMES or _is_private(parsed.hostname or ""):
        return False, "גישה לכתובות פנימיות/פרטיות חסומה (הגנת SSRF)"

    try:
        with httpx.Client(timeout=20, follow_redirects=False) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return True, resp.text[:20000]
    except Exception as exc:
        return False, str(exc)
