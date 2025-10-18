"""Testa o grafo completo do MVP2 com Human-in-the-Loop.

Execute: python src/healthbot/test_graph_mvp2.py
"""

from langchain_core.messages import HumanMessage

from healthbot.graph import create_graph
from healthbot.state import HealthBotState


def main():
    """Executa o fluxo completo do MVP2 com 3 invocações."""
    print("\n")
    print("=" * 70)
    print("🚀 TESTANDO GRAFO MVP2 - HUMAN-IN-THE-LOOP")
    print("=" * 70)
    print()
    
    # Cria o grafo
    app = create_graph()
    
    # Configuração com thread_id (identifica a sessão)
    config = {"configurable": {"thread_id": "test-user-123"}}
    
    # Estado inicial
    initial_state: HealthBotState = {
        "messages": [],
        "topic": None,
        "results": None,
        "summary": None,
    }
    
    try:
        # ==========================================
        # EXECUÇÃO 1: Pergunta o tópico
        # ==========================================
        print("📍 PASSO 1: Perguntando tópico ao usuário")
        print("-" * 70)
        
        # Primeira invocação: executa até a primeira pausa
        app.invoke(initial_state, config)
        
        # Pega o estado atual do checkpointer
        state1 = app.get_state(config)
        
        # Exibe a mensagem do bot
        last_message = state1.values["messages"][-1]
        print(f"\n🤖 HealthBot: {last_message.content}\n")
        
        # Grafo PAUSOU antes de "receive_topic"
        print(f"⏸️  Grafo pausou em: {state1.next}")
        print("-" * 70)
        print()
        
        # ==========================================
        # SIMULAÇÃO: Usuário digita "hipertensão"
        # ==========================================
        print("📍 PASSO 2: Usuário fornece o tópico")
        print("-" * 70)
        
        user_topic = "hipertensão"
        print(f"👤 Usuário: {user_topic}\n")
        
        # ==========================================
        # EXECUÇÃO 2: Processa o tópico e gera resumo
        # ==========================================
        print("🔄 Continuando execução...")
        print("-" * 70)
        
        # IMPORTANTE: Atualiza o estado com o input do usuário
        app.update_state(
            config,
            {"messages": [HumanMessage(content=user_topic)]},
        )
        
        # Continua a execução (passa None para continuar de onde parou)
        app.invoke(None, config)
        
        # Pega o estado atualizado
        state2 = app.get_state(config)
        
        # Grafo executou: receive_topic → search → summarize → present
        # E PAUSOU antes de "wait_ready"
        
        # Exibe o resumo (penúltima mensagem) e a pergunta (última)
        messages = state2.values["messages"]
        summary_msg = messages[-2]
        question_msg = messages[-1]
        
        print(f"\n🤖 HealthBot apresentou o resumo:")
        print(f"{summary_msg.content[:200]}...\n")
        print(f"🤖 {question_msg.content}\n")
        
        print(f"⏸️  Grafo pausou em: {state2.next}")
        print("-" * 70)
        print()
        
        # ==========================================
        # SIMULAÇÃO: Usuário confirma
        # ==========================================
        print("📍 PASSO 3: Usuário confirma prontidão")
        print("-" * 70)
        
        user_confirmation = "pronto"
        print(f"👤 Usuário: {user_confirmation}\n")
        
        # ==========================================
        # EXECUÇÃO 3: Finaliza
        # ==========================================
        print("🔄 Finalizando...")
        print("-" * 70)
        
        # Atualiza o estado com a confirmação
        app.update_state(
            config,
            {"messages": [HumanMessage(content=user_confirmation)]},
        )
        
        # Continua até o fim
        app.invoke(None, config)
        
        # Pega o estado final
        final_state_obj = app.get_state(config)
        final_state = final_state_obj.values
        
        # Grafo executou wait_ready e terminou
        
        print()
        print("=" * 70)
        print("✅ GRAFO MVP2 EXECUTADO COM SUCESSO!")
        print("=" * 70)
        print()
        
        # ==========================================
        # VALIDAÇÃO DO RESULTADO
        # ==========================================
        print("🔍 VALIDAÇÃO DO RESULTADO")
        print("=" * 70)
        
        assert final_state["topic"] is not None, "❌ Topic não foi definido"
        print(f"✅ Topic: {final_state['topic']}")
        
        assert final_state["results"] is not None, "❌ Results não foram preenchidos"
        print(f"✅ Results: {len(final_state['results'])} caracteres")
        
        assert final_state["summary"] is not None, "❌ Summary não foi gerado"
        print(f"✅ Summary: {len(final_state['summary'])} caracteres")
        
        print(f"✅ Total de mensagens: {len(final_state['messages'])}")
        
        print()
        print("=" * 70)
        print("🎉 TESTE COMPLETO PASSOU!")
        print("=" * 70)
        print()
        print("💡 Próximo passo: Implementar interface interativa no main.py")
        
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