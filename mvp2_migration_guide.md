# 🔄 MVP1 → MVP2: Guia de Migração

> **Documento Técnico de Transição**  
> O que muda ao adicionar Human-in-the-Loop

---

## 📊 Visão Geral das Mudanças

### MVP1 (Atual) ✅
```
Execução única e linear:
[START] → [4 nós] → [END]
(~15 segundos de execução contínua)
```

### MVP2 (Próximo) 🎯
```
Execução em 3 etapas com pausas:
[START] → [ask] → PAUSA (input) → [receive] → [search] → [summarize] → [present] → PAUSA (input) → [END]
(Múltiplas invocações do grafo)
```

---

## 🏗️ Mudanças Arquiteturais

### 1. ESTADO: De Simples para Conversacional

#### **MVP1 - Estado Atual:**
```python
class HealthBotState(TypedDict):
    topic: str      # String simples
    results: str    # String simples
    summary: str    # String simples
```

#### **MVP2 - Estado Novo:**
```python
from typing import Annotated
from langgraph.graph.message import add_messages

class HealthBotState(TypedDict):
    # NOVO: Sistema de mensagens para chat
    messages: Annotated[list, add_messages]  # ← Histórico de conversa
    
    # Mantém os campos anteriores
    topic: str
    results: str
    summary: str
```

**O que muda:**
- ✅ **Adiciona** campo `messages` (lista de mensagens)
- ✅ Usa `add_messages` reducer (adiciona sem sobrescrever)
- ✅ Mantém compatibilidade com MVP1

**Por quê:**
- Precisa guardar o histórico de conversa
- Precisa saber o que foi dito antes
- LangGraph usa `messages` para gerenciar chat

---

### 2. NODES: De Hardcoded para Interativo

#### **MVP1 - Nós Atuais:**

```python
# 4 nós, todos executam automaticamente
def set_topic(state):
    return {"topic": "diabetes"}  # ← Hardcoded!

def search_tavily(state):
    # busca...
    
def summarize(state):
    # resume...
    
def print_summary(state):
    # imprime...
```

#### **MVP2 - Nós Novos:**

```python
# 6-7 nós, alguns esperam input do usuário

def ask_topic(state):
    """Pergunta ao usuário o tópico."""
    return {
        "messages": [AIMessage(content="Qual tópico de saúde?")]
    }

def receive_topic(state):
    """Extrai o tópico da resposta do usuário."""
    last_message = state["messages"][-1]  # Última mensagem
    topic = last_message.content          # Conteúdo da mensagem
    return {"topic": topic}

def search_tavily(state):
    # MANTÉM igual ao MVP1
    
def summarize(state):
    # MANTÉM igual ao MVP1
    
def present_summary(state):
    """Mostra o resumo E pergunta se está pronto."""
    return {
        "messages": [
            AIMessage(content=state["summary"]),
            AIMessage(content="Digite 'pronto' quando quiser continuar")
        ]
    }

def wait_for_ready(state):
    """Aguarda confirmação do usuário."""
    # Apenas valida se disse "pronto"
    return {}
```

**O que muda:**
- ❌ **Remove** `set_topic` (hardcoded)
- ✅ **Adiciona** `ask_topic` (pergunta)
- ✅ **Adiciona** `receive_topic` (processa resposta)
- ✅ **Modifica** `present_summary` (adiciona pergunta)
- ✅ **Adiciona** `wait_for_ready` (aguarda confirmação)
- ✅ **Mantém** `search_tavily` e `summarize` iguais

---

### 3. GRAPH: De Linear para Interrompível

#### **MVP1 - Grafo Atual:**

```python
def create_graph():
    workflow = StateGraph(HealthBotState)
    
    workflow.add_node("set_topic", set_topic)
    workflow.add_node("search_tavily", search_tavily)
    workflow.add_node("summarize", summarize)
    workflow.add_node("print_summary", print_summary)
    
    workflow.set_entry_point("set_topic")
    workflow.add_edge("set_topic", "search_tavily")
    workflow.add_edge("search_tavily", "summarize")
    workflow.add_edge("summarize", "print_summary")
    workflow.add_edge("print_summary", END)
    
    # SEM checkpointer!
    return workflow.compile()
```

#### **MVP2 - Grafo Novo:**

```python
from langgraph.checkpoint.memory import MemorySaver

def create_graph():
    workflow = StateGraph(HealthBotState)
    
    # NOVOS nós de interação
    workflow.add_node("ask_topic", ask_topic)
    workflow.add_node("receive_topic", receive_topic)
    workflow.add_node("search_tavily", search_tavily)
    workflow.add_node("summarize", summarize)
    workflow.add_node("present_summary", present_summary)
    workflow.add_node("wait_ready", wait_for_ready)
    
    # Entry point mudou!
    workflow.set_entry_point("ask_topic")
    
    # Novas conexões
    workflow.add_edge("ask_topic", "receive_topic")      # ← NOVO
    workflow.add_edge("receive_topic", "search_tavily")
    workflow.add_edge("search_tavily", "summarize")
    workflow.add_edge("summarize", "present_summary")
    workflow.add_edge("present_summary", "wait_ready")   # ← NOVO
    workflow.add_edge("wait_ready", END)
    
    # CRÍTICO: Adiciona checkpointer e interrupções!
    checkpointer = MemorySaver()
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["receive_topic", "wait_ready"]  # ← PAUSA aqui!
    )
```

**O que muda:**
- ✅ **Adiciona** `checkpointer` (MemorySaver)
- ✅ **Adiciona** `interrupt_before` (lista de nós onde pausa)
- ✅ **Muda** entry point (`set_topic` → `ask_topic`)
- ✅ **Adiciona** 2 novos nós
- ✅ **Reconecta** o fluxo

---

### 4. EXECUÇÃO: De Single-Run para Multi-Step

#### **MVP1 - Execução Atual:**

```python
def run_mvp1():
    app = create_graph()
    
    initial_state = {
        "topic": "",
        "results": "",
        "summary": "",
    }
    
    # UMA única chamada, executa tudo
    final_state = app.invoke(initial_state)
    return final_state
```

#### **MVP2 - Execução Nova:**

```python
def run_mvp2():
    app = create_graph()
    
    # Configuração com thread_id (identifica a sessão)
    config = {"configurable": {"thread_id": "user-123"}}
    
    # Estado inicial
    initial_state = {
        "messages": [],
        "topic": "",
        "results": "",
        "summary": "",
    }
    
    # === PASSO 1: Pergunta o tópico ===
    print("PASSO 1: Perguntando tópico...")
    state1 = app.invoke(initial_state, config)
    # Grafo PAUSA em "receive_topic"
    print(state1["messages"][-1].content)  # "Qual tópico?"
    
    # === PASSO 2: Usuário responde ===
    user_input = input("Você: ")
    state1["messages"].append(HumanMessage(content=user_input))
    
    print("\nPASSO 2: Processando...")
    state2 = app.invoke(state1, config)
    # Grafo executa: receive_topic → search → summarize → present
    # PAUSA em "wait_ready"
    print(state2["messages"][-1].content)  # Resumo + "Digite pronto"
    
    # === PASSO 3: Usuário confirma ===
    user_ready = input("Você: ")
    state2["messages"].append(HumanMessage(content=user_ready))
    
    print("\nPASSO 3: Finalizando...")
    final_state = app.invoke(state2, config)
    # Grafo termina
    
    return final_state
```

**O que muda:**
- ✅ **3 invocações** ao invés de 1
- ✅ Usa `config` com `thread_id`
- ✅ Passa o estado de uma invocação para outra
- ✅ Adiciona mensagens do usuário manualmente

---

## 🆕 Novos Conceitos do MVP2

### 1. **MessagesState e add_messages**

```python
from typing import Annotated
from langgraph.graph.message import add_messages

# Annotated[list, add_messages] significa:
# - É uma lista de mensagens
# - Usa o reducer add_messages
# - ADICIONA mensagens sem sobrescrever as anteriores
```

**Como funciona:**
```python
# Estado inicial
state = {"messages": []}

# Nó 1 adiciona
update1 = {"messages": [AIMessage("Olá")]}
# Resultado: {"messages": [AIMessage("Olá")]}

# Nó 2 adiciona (NÃO sobrescreve!)
update2 = {"messages": [AIMessage("Como vai?")]}
# Resultado: {"messages": [AIMessage("Olá"), AIMessage("Como vai?")]}
```

---

### 2. **Checkpointer (MemorySaver)**

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
```

**O que faz:**
- 💾 **Salva** o estado após cada nó
- 🔄 **Permite** retomar de onde parou
- 🧵 **Usa** `thread_id` para identificar sessões

**Exemplo:**
```python
config = {"configurable": {"thread_id": "user-abc"}}

# Execução 1
app.invoke(state1, config)  # Salva no checkpointer

# Execução 2 (usa o mesmo thread_id)
app.invoke(state2, config)  # Carrega do checkpointer e continua
```

---

### 3. **interrupt_before**

```python
app = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["receive_topic", "wait_ready"]
)
```

**O que faz:**
- ⏸️ **Para** a execução ANTES dos nós especificados
- 💬 **Aguarda** que você adicione input do usuário
- ▶️ **Retoma** quando você chamar `.invoke()` novamente

**Fluxo:**
```
[ask_topic] → PAUSA (antes de receive_topic)
↓ (adiciona input do usuário)
[receive_topic] → [search] → [summarize] → [present] → PAUSA (antes de wait_ready)
↓ (adiciona confirmação)
[wait_ready] → END
```

---

### 4. **thread_id e Sessões**

```python
config = {"configurable": {"thread_id": "user-123"}}
```

**Por quê usar:**
- 👤 **Identifica** diferentes usuários
- 💾 **Separa** estados de cada usuário
- 🔄 **Permite** múltiplas conversas simultâneas

**Exemplo:**
```python
# Usuário A
config_a = {"configurable": {"thread_id": "user-a"}}
app.invoke(state_a, config_a)

# Usuário B (estado separado!)
config_b = {"configurable": {"thread_id": "user-b"}}
app.invoke(state_b, config_b)
```

---

## 🔨 Refatorações Necessárias

### Arquivo: `state.py`

**Antes (MVP1):**
```python
class HealthBotState(TypedDict):
    topic: str
    results: str
    summary: str
```

**Depois (MVP2):**
```python
from typing import Annotated
from langgraph.graph.message import add_messages

class HealthBotState(TypedDict):
    messages: Annotated[list, add_messages]  # ← ADICIONAR
    topic: str
    results: str
    summary: str
```

---

### Arquivo: `nodes.py`

**Adicionar:**
```python
from langchain_core.messages import AIMessage, HumanMessage

def ask_topic(state: HealthBotState) -> dict:
    """Pergunta ao usuário o tópico."""
    return {
        "messages": [AIMessage(content="Qual tópico de saúde você quer aprender?")]
    }

def receive_topic(state: HealthBotState) -> dict:
    """Extrai o tópico da última mensagem do usuário."""
    last_message = state["messages"][-1]
    topic = last_message.content
    return {"topic": topic}

def wait_for_ready(state: HealthBotState) -> dict:
    """Aguarda confirmação do usuário."""
    return {}
```

**Modificar:**
```python
def present_summary(state: HealthBotState) -> dict:
    """Apresenta o resumo E pergunta se está pronto."""
    summary = state["summary"]
    return {
        "messages": [
            AIMessage(content=summary),
            AIMessage(content="\nDigite 'pronto' quando quiser continuar.")
        ]
    }
```

**Remover:**
```python
# ❌ Deletar esta função (não precisa mais)
def set_topic(state: HealthBotState) -> dict:
    return {"topic": "diabetes"}
```

---

### Arquivo: `graph.py`

**Antes (MVP1):**
```python
def create_graph():
    workflow = StateGraph(HealthBotState)
    
    workflow.add_node("set_topic", set_topic)
    # ...
    
    workflow.set_entry_point("set_topic")
    # ...
    
    return workflow.compile()  # SEM checkpointer
```

**Depois (MVP2):**
```python
from langgraph.checkpoint.memory import MemorySaver

def create_graph():
    workflow = StateGraph(HealthBotState)
    
    # Novos nós
    workflow.add_node("ask_topic", ask_topic)
    workflow.add_node("receive_topic", receive_topic)
    workflow.add_node("search_tavily", search_tavily)
    workflow.add_node("summarize", summarize)
    workflow.add_node("present_summary", present_summary)
    workflow.add_node("wait_ready", wait_for_ready)
    
    # Novo entry point
    workflow.set_entry_point("ask_topic")
    
    # Novas conexões
    workflow.add_edge("ask_topic", "receive_topic")
    workflow.add_edge("receive_topic", "search_tavily")
    workflow.add_edge("search_tavily", "summarize")
    workflow.add_edge("summarize", "present_summary")
    workflow.add_edge("present_summary", "wait_ready")
    workflow.add_edge("wait_ready", END)
    
    # NOVO: Checkpointer e interrupções
    checkpointer = MemorySaver()
    return workflow.compile(
        checkpointer=checkpointer,
        interrupt_before=["receive_topic", "wait_ready"]
    )
```

---

## 📚 O que estudar ANTES do MVP2

### 1. **LangGraph - Messages**
- [Documentação: Managing Conversation History](https://langchain-ai.github.io/langgraph/how-tos/manage-conversation-history/)
- Entender `MessagesState`
- Entender `add_messages` reducer

### 2. **LangGraph - Persistence**
- [Documentação: Persistence](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- Entender `MemorySaver`
- Entender `thread_id`

### 3. **LangGraph - Human-in-the-Loop**
- [Documentação: Human-in-the-Loop](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- Entender `interrupt_before`
- Entender múltiplas invocações

### 4. **LangChain - Messages**
- [Documentação: Message Types](https://python.langchain.com/docs/concepts/messages/)
- `AIMessage` vs `HumanMessage`
- Como acessar `message.content`

---

## ✅ Checklist de Preparação para MVP2

Antes de começar a implementar, certifique-se de entender:

- [ ] Por que precisa de `messages` no estado
- [ ] O que é um "reducer" (`add_messages`)
- [ ] Como funciona o `MemorySaver`
- [ ] Por que precisa de `thread_id`
- [ ] O que `interrupt_before` faz
- [ ] Como fazer múltiplas invocações do grafo
- [ ] Diferença entre `AIMessage` e `HumanMessage`
- [ ] Como extrair conteúdo da última mensagem

---

## 🎯 Próximos Passos

Quando estiver pronto para implementar o MVP2:

1. ✅ Ler este documento
2. ✅ Estudar os links de documentação
3. ✅ Revisar o código do MVP1
4. ✅ Fazer perguntas sobre o que não ficou claro
5. 🚀 Implementar MVP2 com tutorial passo a passo

---

**Boa revisão e estudos!** 📚

Quando voltar, estarei aqui para guiar cada passo do MVP2! 💪