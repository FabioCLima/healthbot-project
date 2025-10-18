"""Configurações do HealthBot.

Gerencia variáveis de ambiente e configurações do projeto.
"""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Carrega o .env da raiz do projeto
PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Força o carregamento do .env
load_dotenv(dotenv_path=ENV_FILE, override=True)


class Settings(BaseSettings):  # type: ignore[misc]
    """Configurações da aplicação HealthBot."""

    # OpenAI
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    # Tavily
    tavily_api_key: str = Field(..., alias="TAVILY_API_KEY")

    # LangSmith (opcional)  # noqa: ERA001
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com", alias="LANGCHAIN_ENDPOINT"
    )
    langchain_api_key: str | None = Field(default=None, alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(
        default="HealthBot Prototype - Fabio Lima", alias="LANGCHAIN_PROJECT"
    )

    model_config = SettingsConfigDict(  # type: ignore[assignment]
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def validate_required_keys(self) -> tuple[bool, list[str]]:
        """Valida se as API keys obrigatórias estão configuradas.

        Returns:
            Tupla (sucesso, lista_de_erros)

        """
        errors: list[str] = []

        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY não está configurada")

        if not self.tavily_api_key:
            errors.append("TAVILY_API_KEY não está configurada")

        return len(errors) == 0, errors

    def setup_environment(self) -> None:
        """Configura as variáveis de ambiente do sistema.

        Necessário para algumas bibliotecas que leem diretamente do os.environ.
        """
        os.environ["OPENAI_API_KEY"] = self.openai_api_key
        os.environ["TAVILY_API_KEY"] = self.tavily_api_key

        if self.langchain_tracing_v2:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_ENDPOINT"] = self.langchain_endpoint
            if self.langchain_api_key:
                os.environ["LANGCHAIN_API_KEY"] = self.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.langchain_project


# Instância global de configurações
settings = Settings()  # type: ignore[call-arg]

# Configura o ambiente automaticamente ao importar
settings.setup_environment()
