import hmac

from fastapi import Depends, FastAPI, Form
from fastapi.responses import HTMLResponse

from app.auth import verify_token
from app.config import settings
from app.models import TaskRequest, TaskResponse
from app.orchestrator import run_agent
from app.settings_store import set_values

app = FastAPI(title="Autonomous Server Agent")

CHAT_PAGE = """<!doctype html>
<html lang="he" dir="rtl">
<head><meta charset="utf-8"><title>צ'אט עם הסוכן</title></head>
<body style="font-family: sans-serif; max-width: 640px; margin: 40px auto;">
<h2>צ'אט עם הסוכן</h2>
<label>טוקן אימות (AGENT_AUTH_TOKEN)<br>
  <input type="password" id="token" style="width:100%"></label><br><br>
<label>משימה / שאלה<br>
  <textarea id="goal" rows="3" style="width:100%"></textarea></label><br><br>
<button onclick="send()">שליחה</button>
<a href="/settings" style="margin-right:12px">הגדרות</a>
<p id="status"></p>
<div id="output" style="white-space:pre-wrap; background:#f5f5f5; padding:12px; border-radius:6px; margin-top:16px;"></div>
<script>
  const tokenInput = document.getElementById("token");
  tokenInput.value = localStorage.getItem("agent_token") || "";
  async function send() {
    const token = tokenInput.value;
    localStorage.setItem("agent_token", token);
    const goal = document.getElementById("goal").value;
    const status = document.getElementById("status");
    const output = document.getElementById("output");
    status.textContent = "שולח...";
    output.textContent = "";
    try {
      const resp = await fetch("/task", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ goal: goal }),
      });
      const data = await resp.json();
      if (!resp.ok) {
        status.textContent = "שגיאה: " + resp.status;
        output.textContent = JSON.stringify(data, null, 2);
        return;
      }
      status.textContent = "התקבלה תשובה";
      const lines = (data.steps || []).map((s) => "[" + s.type + "] " + s.content);
      lines.push("");
      lines.push("תשובה סופית: " + data.final_answer);
      output.textContent = lines.join("\\n");
    } catch (err) {
      status.textContent = "שגיאת רשת: " + err;
    }
  }
</script>
</body></html>"""

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
    <select name="llm_provider" id="provider" style="width:100%" onchange="updateModels()">
      <option value="">(ללא שינוי)</option>
      <option value="groq">groq</option>
      <option value="gemini">gemini</option>
    </select></label><br><br>
  <label>LLM_MODEL<br>
    <select name="llm_model" id="model" style="width:100%"></select></label><br><br>
  <button type="submit">שמירה</button>
</form>
<a href="/">חזרה לצ'אט</a>
{message}
<script>
  const MODELS = {{
    groq: ["llama-3.1-8b-instant", "llama-3.3-70b-versatile", "gemma2-9b-it"],
    gemini: ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"],
  }};
  function updateModels() {{
    const provider = document.getElementById("provider").value;
    const modelSelect = document.getElementById("model");
    modelSelect.innerHTML = "";
    const noChange = document.createElement("option");
    noChange.value = "";
    noChange.textContent = "(ללא שינוי)";
    modelSelect.appendChild(noChange);
    (MODELS[provider] || []).forEach((m) => {{
      const opt = document.createElement("option");
      opt.value = m;
      opt.textContent = m;
      modelSelect.appendChild(opt);
    }});
  }}
  updateModels();
</script>
</body></html>"""


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def chat_page() -> str:
    return CHAT_PAGE


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
