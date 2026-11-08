import hmac

from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse

from app.auth import verify_token
from app.config import settings
from app.models import TaskRequest, TaskResponse
from app.orchestrator import run_agent
from app.settings_store import set_values

app = FastAPI(title="Autonomous Server Agent")

SETTINGS_PAGE = """<!doctype html>
<html lang="he" dir="rtl">
<head><meta charset="utf-8"><title>הגדרות סוכן</title></head>
<body style="font-family: sans-serif; max-width: 480px; margin: 40px auto;">
<h2>הגדרות סוכן</h2>
<form method="post" action="/settings">
  <label>טוקן אימות (AGENT_AUTH_TOKEN)<br>
    <input type="password" name="token" required style="width:100%"></label><br><br>
  <label>LLM_API_KEY<br>
    <input type="password" name="llm_api_key" style="width:100%"></label><br><br>
  <label>LLM_PROVIDER<br>
    <input type="text" name="llm_provider" placeholder="groq / gemini" style="width:100%"></label><br><br>
  <label>LLM_MODEL<br>
    <input type="text" name="llm_model" style="width:100%"></label><br><br>
  <button type="submit">שמירה</button>
</form>
{message}
</body></html>"""


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/settings", response_class=HTMLResponse)
def settings_page() -> str:
    return SETTINGS_PAGE.format(message="")


@app.post("/settings", response_class=HTMLResponse)
def update_settings(
    token: str = Form(...),
    llm_api_key: str = Form(""),
    llm_provider: str = Form(""),
    llm_model: str = Form(""),
) -> str:
    if not hmac.compare_digest(token, settings.agent_auth_token):
        return SETTINGS_PAGE.format(message="<p style='color:red'>טוקן שגוי</p>")
    set_values({"llm_api_key": llm_api_key, "llm_provider": llm_provider, "llm_model": llm_model})
    return SETTINGS_PAGE.format(message="<p style='color:green'>נשמר בהצלחה</p>")


@app.post("/task", response_model=TaskResponse, dependencies=[Depends(verify_token)])
async def create_task(request: TaskRequest) -> TaskResponse:
    steps = await run_agent(request.goal)
    final = next((s.content for s in reversed(steps) if s.type == "final"), "")
    return TaskResponse(steps=steps, final_answer=final)
