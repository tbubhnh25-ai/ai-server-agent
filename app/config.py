from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    agent_auth_token: str

    llm_provider: str = "ollama"
    llm_model: str = "llama3.1"
    ollama_base_url: str = "http://ollama:11434"
    llm_api_key: str = ""

    sandbox_image: str = "agent-sandbox:latest"
    workspace_dir: str = "/workspace"

    max_loop_iterations: int = 15
    shell_timeout_seconds: int = 60
    sandbox_memory_limit: str = "512m"
    sandbox_cpu_limit: float = 1.0

    class Config:
        env_file = ".env"


settings = Settings()
