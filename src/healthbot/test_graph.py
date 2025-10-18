"""Testa o grafo completo do MVP1.

Execute: python src/healthbot/test_graph.py
"""

import traceback

from healthbot.graph import run_mvp1


def main() -> None:
    """Executa o MVP1 completo.
    
    Raises:
        ValueError: Se algum campo obrigatório não foi preenchido

    """
    print("\n")
    print("🧪 INICIANDO TESTE DO GRAFO COMPLETO - MVP1")
    print("\n")

    try:
        # Executa o fluxo completo
        final_state = run_mvp1()

        # Valida o resultado
        print("\n")
        print("=" * 70)
        print("🔍 VALIDAÇÃO DO RESULTADO")
        print("=" * 70)
        print()

        if not final_state["topic"]:
            raise ValueError("❌ Topic não foi definido")
        print(f"✅ Topic: {final_state['topic']}")

        if not final_state["results"]:
            raise ValueError("❌ Results não foi preenchido")
        print(f"✅ Results: {len(final_state['results'])} caracteres")

        if not final_state["summary"]:
            raise ValueError("❌ Summary não foi gerado")
        print(f"✅ Summary: {len(final_state['summary'])} caracteres")

        print()
        print("=" * 70)
        print("🎉 TESTE COMPLETO PASSOU!")
        print("=" * 70)

    except ValueError as e:
        print()
        print("=" * 70)
        print("❌ ERRO DE VALIDAÇÃO")
        print("=" * 70)
        print(f"Erro: {e}")
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO NO TESTE")
        print("=" * 70)
        print(f"Erro: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
