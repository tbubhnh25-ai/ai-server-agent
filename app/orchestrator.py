import json
import uuid

from app.audit import log_event
from app.config import settings
from app.llm_provider import get_provider
from app.models import AgentStep, ToolCall, ToolResult
from app.tools import TOOL_DESCRIPTIONS, TOOLS

SYSTEM_PROMPT = f"""אתה סוכן אוטונומי שפועל על שרת לינוקס דרך כלים.
{TOOL_DESCRIPTIONS}

בכל תור, הגב בבלוק JSON יחיד ובלבד, באחת משתי צורות:
1. פעולה: {{"thought": "...", "action": {{"tool": "<שם הכלי>", "args": {{...}}}}}}
2. תשובה סופית: {{"thought": "...", "final_answer": "..."}}

אל תוסיף טקסט מחוץ ל-JSON."""


def _parse_llm_json(raw: str) -> dict:
    start = raw.find("{")
    end = raw.rfind("}")
    return json.loads(raw[start : end + 1])


async def run_agent(goal: str) -> list[AgentStep]:
    task_id = uuid.uuid4().hex
    log_event(task_id, "task_start", {"goal": goal})

    provider = get_provider()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": goal},
    ]
    steps: list[AgentStep] = []

    for _ in range(settings.max_loop_iterations):
        raw = await provider.chat(messages)
        try:
            parsed = _parse_llm_json(raw)
        except (json.JSONDecodeError, ValueError):
            steps.append(AgentStep(type="thought", content=f"פלט לא תקין מהמודל: {raw}"))
            log_event(task_id, "invalid_llm_output", {"raw": raw})
            break

        thought = parsed.get("thought", "")
        steps.append(AgentStep(type="thought", content=thought))
        log_event(task_id, "thought", {"thought": thought})
        messages.append({"role": "assistant", "content": raw})

        if "final_answer" in parsed:
            steps.append(AgentStep(type="final", content=parsed["final_answer"]))
            log_event(task_id, "task_end", {"final_answer": parsed["final_answer"]})
            return steps

        action = parsed.get("action")
        if not action:
            steps.append(AgentStep(type="final", content="המודל לא סיפק פעולה או תשובה סופית"))
            log_event(task_id, "task_end", {"final_answer": None, "reason": "no_action_no_final_answer"})
            return steps

        tool_call = ToolCall(tool=action["tool"], args=action.get("args", {}))
        steps.append(AgentStep(type="action", content=tool_call.tool, tool_call=tool_call))
        log_event(task_id, "action", {"tool": tool_call.tool, "args": tool_call.args})

        tool_fn = TOOLS.get(tool_call.tool)
        if tool_fn is None:
            result = ToolResult(tool=tool_call.tool, ok=False, output="", error="כלי לא קיים")
        else:
            try:
                ok, output = tool_fn(tool_call.args)
                result = ToolResult(tool=tool_call.tool, ok=ok, output=output, error=None if ok else output)
            except Exception as exc:
                result = ToolResult(tool=tool_call.tool, ok=False, output="", error=str(exc))

        steps.append(AgentStep(type="observation", content=result.output or result.error or "", tool_result=result))
        log_event(task_id, "observation", {"tool": result.tool, "ok": result.ok, "output": result.output, "error": result.error})
        messages.append({"role": "user", "content": f"Observation: {result.model_dump_json()}"})

    steps.append(AgentStep(type="final", content="הגעה למספר האיטרציות המקסימלי בלי תשובה סופית"))
    log_event(task_id, "task_end", {"final_answer": None, "reason": "max_iterations_reached"})
    return steps
