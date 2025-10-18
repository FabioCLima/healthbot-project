"""Script para testar as configurações do HealthBot.

Execute: python src/healthbot/test_configurations.py
"""

import sys

from healthbot.settings import ENV_FILE, PROJECT_ROOT, settings


def main() -> int:
    """Testa se as configurações estão corretas."""
    print("=" * 70)
    print("🔍 VERIFICANDO CONFIGURAÇÕES DO HEALTHBOT")
    print("=" * 70)
    print()

    # Mostra onde encontrou o .env
    print("📁 Informações do ambiente:")
    print(f"   Raiz do projeto: {PROJECT_ROOT}")
    print(f"   Arquivo .env: {ENV_FILE}")
    print(f"   .env existe? {'✅ Sim' if ENV_FILE.exists() else '❌ Não'}")
    print()

    # Valida as chaves obrigatórias
    is_valid, errors = settings.validate_required_keys()

    if not is_valid:
        print("❌ ERRO: Configurações inválidas!\n")
        for error in errors:
            print(f"   {error}")
        print()
        print("💡 Solução: Verifique seu arquivo .env na raiz do projeto")
        print()
        return 1

    # Mostra as configurações (mascarando as chaves)
    print("✅ Configurações carregadas com sucesso!\n")

    print("📋 OPENAI")
    print(f"   API Key: ...{settings.openai_api_key[-10:]}")
    print(f"   Modelo: {settings.openai_model}")
    print()

    print("📋 TAVILY")
    print(f"   API Key: ...{settings.tavily_api_key[-10:]}")
    print()

    print("📋 LANGCHAIN/LANGSMITH (Debug - Opcional)")
    if settings.langchain_tracing_v2:
        print("   Tracing: ✅ Habilitado")
        print(f"   Endpoint: {settings.langchain_endpoint}")
        if settings.langchain_api_key:
            print(f"   API Key: ...{settings.langchain_api_key[-10:]}")
        print(f"   Project: {settings.langchain_project}")
    else:
        print("   Tracing: ❌ Desabilitado")
    print()

    print("=" * 70)
    print("🎉 TUDO PRONTO PARA COMEÇAR O DESENVOLVIMENTO!")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
