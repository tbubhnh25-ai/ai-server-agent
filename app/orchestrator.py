import json

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
            break

        thought = parsed.get("thought", "")
        steps.append(AgentStep(type="thought", content=thought))
        messages.append({"role": "assistant", "content": raw})

        if "final_answer" in parsed:
            steps.append(AgentStep(type="final", content=parsed["final_answer"]))
            return steps

        action = parsed.get("action")
        if not action:
            steps.append(AgentStep(type="final", content="המודל לא סיפק פעולה או תשובה סופית"))
            return steps

        tool_call = ToolCall(tool=action["tool"], args=action.get("args", {}))
        steps.append(AgentStep(type="action", content=tool_call.tool, tool_call=tool_call))

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
        messages.append({"role": "user", "content": f"Observation: {result.model_dump_json()}"})

    steps.append(AgentStep(type="final", content="הגעה למספר האיטרציות המקסימלי בלי תשובה סופית"))
    return steps
