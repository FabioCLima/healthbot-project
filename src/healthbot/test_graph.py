"""
Testa o grafo completo do MVP1.
Execute: python src/healthbot/test_graph.py
"""

from healthbot.graph import run_mvp1


def main():
    """Executa o MVP1 completo."""
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

        assert final_state["topic"] != "", "❌ Topic não foi definido"
        print(f"✅ Topic: {final_state['topic']}")

        assert final_state["results"] != "", "❌ Results não foi preenchido"
        print(f"✅ Results: {len(final_state['results'])} caracteres")

        assert final_state["summary"] != "", "❌ Summary não foi gerado"
        print(f"✅ Summary: {len(final_state['summary'])} caracteres")

        print()
        print("=" * 70)
        print("🎉 TESTE COMPLETO PASSOU!")
        print("=" * 70)

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO NO TESTE")
        print("=" * 70)
        print(f"Erro: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()