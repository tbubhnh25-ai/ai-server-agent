from typing import Any, Literal
from pydantic import BaseModel


class TaskRequest(BaseModel):
    goal: str


class ToolCall(BaseModel):
    tool: str
    args: dict[str, Any]


class ToolResult(BaseModel):
    tool: str
    ok: bool
    output: str
    error: str | None = None


class AgentStep(BaseModel):
    type: Literal["thought", "action", "observation", "final"]
    content: str
    tool_call: ToolCall | None = None
    tool_result: ToolResult | None = None


class TaskResponse(BaseModel):
    steps: list[AgentStep]
    final_answer: str
