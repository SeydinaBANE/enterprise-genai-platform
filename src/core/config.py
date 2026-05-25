from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # LLM
    openrouter_api_key: str = ""
    llm_model: str = "openai/gpt-4o-mini"
    embedding_model: str = "openai/text-embedding-3-small"

    # Vector store
    chroma_persist_dir: str = "./data/chroma"
    azure_search_endpoint: str = ""
    azure_search_api_key: str = ""
    azure_search_index_name: str = "genai-platform"

    # Security
    jwt_secret_key: str = "change_me"  # noqa: S105
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    azure_content_safety_endpoint: str = ""
    azure_content_safety_api_key: str = ""

    # Observability
    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "genai-platform"

    # API
    api_host: str = "0.0.0.0"  # noqa: S104
    api_port: int = 8000
    log_level: str = "INFO"

    # MCP
    mcp_server_port: int = 8001

    @property
    def use_azure_search(self) -> bool:
        return bool(self.azure_search_endpoint and self.azure_search_api_key)

    @property
    def litellm_api_base(self) -> str:
        return "https://openrouter.ai/api/v1"


settings = Settings()
