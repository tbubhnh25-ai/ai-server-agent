from fastapi import Depends, FastAPI

from app.auth import verify_token
from app.models import TaskRequest, TaskResponse
from app.orchestrator import run_agent

app = FastAPI(title="Autonomous Server Agent")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/task", response_model=TaskResponse, dependencies=[Depends(verify_token)])
async def create_task(request: TaskRequest) -> TaskResponse:
    steps = await run_agent(request.goal)
    final = next((s.content for s in reversed(steps) if s.type == "final"), "")
    return TaskResponse(steps=steps, final_answer=final)
