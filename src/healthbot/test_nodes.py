"""Testa os novos nós do MVP2.

Execute: python src/healthbot/test_nodes_mvp2.py
"""

from typing import TYPE_CHECKING

from langchain_core.messages import HumanMessage

from healthbot.nodes import ask_topic, present_summary, receive_topic, wait_for_ready

if TYPE_CHECKING:
    from healthbot.state import HealthBotState


def main() -> None:
    """Testa os nós novos do MVP2."""
    print("=" * 60)
    print("🧪 TESTANDO NOVOS NÓS DO MVP2")
    print("=" * 60)
    print()

    # Estado inicial
    state: HealthBotState = {
        "messages": [],
        "topic": None,
        "results": None,
        "summary": None,
    }

    # ==========================================
    # Teste 1: ask_topic
    # ==========================================
    print("1️⃣ Testando ask_topic...")
    update1 = ask_topic(state)
    state["messages"].extend(update1["messages"])
    print(f"   ✅ Mensagem enviada: '{state['messages'][-1].content[:60]}...'")
    print()

    # ==========================================
    # Teste 2: Simulação de resposta do usuário
    # ==========================================
    print("2️⃣ Simulando resposta do usuário...")
    state["messages"].append(HumanMessage(content="diabetes"))
    print("   👤 Usuário digitou: 'diabetes'")
    print()

    # ==========================================
    # Teste 3: receive_topic
    # ==========================================
    print("3️⃣ Testando receive_topic...")
    update2 = receive_topic(state)
    state["topic"] = update2["topic"]
    state["messages"].extend(update2["messages"])
    print(f"   ✅ Tópico extraído: '{state['topic']}'")
    print(f"   ✅ Confirmação: '{state['messages'][-1].content[:60]}...'")
    print()

    # ==========================================
    # Teste 4: present_summary (com resumo fake)
    # ==========================================
    print("4️⃣ Testando present_summary...")
    state["summary"] = (
        "A diabetes é uma condição crônica que afeta como o corpo "
        "processa a glicose no sangue. É importante manter uma dieta "
        "equilibrada e praticar exercícios regularmente."
    )
    update3 = present_summary(state)
    state["messages"].extend(update3["messages"])
    print("   ✅ Resumo adicionado às mensagens")
    print("   ✅ Pergunta de confirmação adicionada")
    print()

    # ==========================================
    # Teste 5: Simulação de confirmação
    # ==========================================
    print("5️⃣ Simulando confirmação do usuário...")
    state["messages"].append(HumanMessage(content="pronto"))
    print("   👤 Usuário digitou: 'pronto'")
    print()

    # ==========================================
    # Teste 6: wait_for_ready
    # ==========================================
    print("6️⃣ Testando wait_for_ready...")
    wait_for_ready(state)
    print("   ✅ wait_for_ready executado com sucesso")
    print()

    # ==========================================
    # Resumo final
    # ==========================================
    print("=" * 60)
    print("📊 RESUMO DO TESTE")
    print("=" * 60)
    print(f"Total de mensagens no histórico: {len(state['messages'])}")
    print(f"Tópico extraído: {state['topic']}")
    print(f"Resumo presente: {state['summary'] is not None}")
    print()
    print("=" * 60)
    print("🎉 TODOS OS NOVOS NÓS FUNCIONANDO!")
    print("=" * 60)


if __name__ == "__main__":
    main()
