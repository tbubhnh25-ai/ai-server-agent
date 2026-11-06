from fastapi import Header, HTTPException

from app.config import settings


def verify_token(authorization: str = Header(default="")) -> None:
    expected = f"Bearer {settings.agent_auth_token}"
    if not authorization or authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing bearer token")
