from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    agent_auth_token: str

    llm_provider: str = "groq"
    llm_model: str = "llama-3.1-8b-instant"
    llm_api_key: str = ""

    workspace_dir: str = "/app/workspace"
    audit_log_path: str = "/app/workspace/audit.log"

    max_loop_iterations: int = 15
    shell_timeout_seconds: int = 60
    sandbox_memory_limit_mb: int = 512

    class Config:
        env_file = ".env"


settings = Settings()
