# 🏗️ HealthBot - Arquitetura e MVPs

> **Documento de Referência Técnica**  
> Planejamento incremental do projeto HealthBot usando LangGraph

---

## 📅 Timeline do Projeto

- **Início:** 17/10/2025
- **Deadline MVP Final:** 25/10/2025
- **Testes e Validação:** 25-28/10/2025
- **Submissão:** 29/10/2025

**Total: 8 dias de desenvolvimento**

---

## 🎯 Análise Técnica do Projeto

### Tipo de Agente: Workflow Orquestrado

O HealthBot **NÃO é um agente ReAct clássico**. Características:

#### ReAct Pattern (NÃO usaremos)
- Loop iterativo: Pensa → Age → Observa → Repensa
- Decisão dinâmica de ferramentas
- Exemplo: Agente que decide se precisa buscar, calcular, ou acessar DB

#### HealthBot (O que É)
- ✅ Fluxo **DETERMINÍSTICO** (caminho fixo)
- ✅ Ferramenta única e previsível (Tavily)
- ✅ **Workflow Orquestrado** com interações humanas
- ✅ Estado que persiste entre etapas

---

## 🎨 Padrões de Design Utilizados

### 1. Sequential Chain Pattern
**Quando:** MVP 1-2  
**O que é:** Fluxo linear de transformações de dados  
```
Input → Tool → LLM → Output
```

### 2. Human-in-the-Loop Pattern
**Quando:** MVP 2-4  
**O que é:** Pausas para input do usuário  
```
Agent → PAUSE → Wait User Input → Continue
```

### 3. Conditional Router Pattern
**Quando:** MVP 4  
**O que é:** Decisões que alteram o fluxo  
```
       ┌─ Option A → Path A
Router ┤
       └─ Option B → Path B
```

### 4. Stateful Workflow Pattern
**Quando:** Todos os MVPs  
**O que é:** Estado compartilhado entre todos os nós  

---

## 📐 Arquitetura Detalhada por MVP

### MVP 1: Sequential Chain (Linear Puro) ✅
**Objetivo:** Integração Tavily + OpenAI funcionando  
**Duração:** 3 horas  
**Status:** ✅ **COMPLETO** (18/10/2025)

```python
# Estado
Estado: {
    topic: str,        # Ex: "diabetes"
    results: str,      # Resultados do Tavily
    summary: str       # Resumo do LLM
}

# Grafo
[START] 
   ↓
[set_topic] ← Hardcoded "diabetes"
   ↓
[search_tavily] ← Tool: TavilySearchResults
   ↓
[summarize] ← LLM: ChatOpenAI
   ↓
[print_summary]
   ↓
[END]
```

**Conceitos técnicos implementados:**
- ✅ Estado tipado (TypedDict)
- ✅ Nós como funções puras
- ✅ Tool calling (Tavily)
- ✅ LLM prompting
- ✅ Busca automática de .env
- ✅ Validação de configurações

**Arquivos criados:**
- ✅ `src/healthbot/settings.py` - Configurações com busca automática
- ✅ `src/healthbot/state.py` - Definição do Estado
- ✅ `src/healthbot/nodes.py` - Nós do grafo
- ✅ `src/healthbot/graph.py` - Construção do grafo
- ✅ Testes para cada componente

**Entregável:** ✅ Script que busca info sobre "diabetes" e mostra resumo profissional

**Resultado real:**
```
Topic: diabetes
Results: 3318 caracteres de fontes confiáveis
Summary: 1376 caracteres - resumo educacional de qualidade
```

---

### MVP 2: Human-in-the-Loop
**Objetivo:** Adicionar interação com usuário  
**Duração:** 4 horas  
**Status:** ⬜ Não iniciado

```python
# Estado
Estado: {
    messages: list,    # ← NOVO: Histórico de conversa
    topic: str,
    results: str,
    summary: str
}

# Grafo
[START]
   ↓
[ask_topic] ← Pergunta "Qual tópico?"
   ↓
[INTERRUPT] ← PARA e espera input
   ↓
[receive_topic] ← Processa input do usuário
   ↓
[search_tavily]
   ↓
[summarize]
   ↓
[present_summary]
   ↓
[ask_ready] ← Pergunta "Digite 'pronto'"
   ↓
[INTERRUPT]
   ↓
[END]
```

**Conceitos técnicos novos:**
- ⬜ `checkpointer` (salvar estado entre execuções)
- ⬜ `.invoke()` com interrupções
- ⬜ `MessagesState` do LangGraph
- ⬜ `thread_id` para sessões

**Entregável:**
- Bot interativo que pergunta tópico e aguarda confirmação

---

### MVP 3: Sistema de Quiz Completo
**Objetivo:** Implementar geração, apresentação e avaliação de quiz  
**Duração:** 5 horas  
**Status:** ⬜ Não iniciado

```python
# Estado
Estado: {
    messages: list,
    topic: str,
    results: str,
    summary: str,
    quiz_question: str,  # ← NOVO
    quiz_answer: str,    # ← NOVO
    grade: dict          # ← NOVO: {score: int, feedback: str}
}

# Grafo
[...MVP 2...]
   ↓
[create_quiz] ← LLM gera pergunta baseada no summary
   ↓
[present_quiz] ← Mostra pergunta ao usuário
   ↓
[INTERRUPT]
   ↓
[receive_answer] ← Captura resposta
   ↓
[grade_answer] ← LLM avalia com citações do summary
   ↓
[present_grade] ← Mostra nota e feedback
   ↓
[END]
```

**Conceitos técnicos novos:**
- ⬜ Prompt engineering avançado (gerar quiz estruturado)
- ⬜ Citation/grounding (avaliar com citações)
- ⬜ Structured output do LLM
- ⬜ Comparação semântica de respostas

**Entregável:**
- Fluxo completo: busca → resumo → quiz → avaliação

---

### MVP 4: Conditional Routing + Loop
**Objetivo:** Permitir múltiplas sessões e decisão de saída  
**Duração:** 3 horas  
**Status:** ⬜ Não iniciado

```python
# Estado
Estado: {
    ...tudo anterior...,
    continue_session: bool  # ← NOVO
}

# Grafo
[...MVP 3...]
   ↓
[ask_continue] ← "Novo tópico ou sair?"
   ↓
[INTERRUPT]
   ↓
[receive_continue_choice]
   ↓
[should_continue?] ← CONDITIONAL EDGE
   ↓           ↓
  SIM         NÃO
   ↓           ↓
[reset_state] [END]
   ↓
[ask_topic] ← VOLTA PRO INÍCIO (ciclo)
```

**Conceitos técnicos novos:**
- ⬜ `add_conditional_edges()` (roteamento)
- ⬜ Função de decisão (retorna "continue" ou "end")
- ⬜ Reset seletivo do estado
- ⬜ Grafos cíclicos (não é mais DAG puro)

**Entregável:**
- Sistema completo com loop funcional

---

## 🔧 Stack Técnico por MVP

| MVP | Estado | Nós | Edges | LLM | Tools | Human Input | Checkpoint | Conditional | Status |
|-----|--------|-----|-------|-----|-------|-------------|------------|-------------|--------|
| 1   | Básico | 4 | Linear | ✅ | Tavily | ❌ | ❌ | ❌ | **✅ COMPLETO** |
| 2   | +Messages | 6-7 | Linear | ✅ | Tavily | ✅ | ✅ | ❌ | ⬜ Próximo |
| 3   | +Quiz | 10-11 | Linear | ✅ | Tavily | ✅ | ✅ | ❌ | ⬜ Pendente |
| 4   | +Continue | 12-13 | **Condicional** | ✅ | Tavily | ✅ | ✅ | ✅ | ⬜ Pendente |

---

## 🎓 Conhecimentos por MVP

### MVP 1 - Tools + LLM ✅
```python
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

tavily = TavilySearchResults(max_results=3)
llm = ChatOpenAI(model="gpt-4o-mini")

def search_node(state):
    results = tavily.invoke({"query": state["topic"]})
    return {"results": str(results)}

def summarize_node(state):
    response = llm.invoke(f"Resuma: {state['results']}")
    return {"summary": response.content}
```

### MVP 2 - Checkpointer + Interrupts
```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer, interrupt_before=["receive_topic"])

# Executar com thread_id
config = {"configurable": {"thread_id": "user-123"}}
app.invoke(initial_state, config)
```

### MVP 3 - Prompt Engineering
```python
from langchain_core.messages import SystemMessage, HumanMessage

def create_quiz(state):
    prompt = [
        SystemMessage(content="Você é um educador médico..."),
        HumanMessage(content=f"Crie uma pergunta sobre: {state['summary']}")
    ]
    response = llm.invoke(prompt)
    return {"quiz_question": response.content}
```

### MVP 4 - Conditional Edges
```python
def should_continue(state) -> str:
    if state["continue_session"]:
        return "continue"
    return "end"

graph.add_conditional_edges(
    "receive_continue_choice",
    should_continue,
    {
        "continue": "reset_state",
        "end": END
    }
)
```

---

## 🚫 O que NÃO vamos usar

| Conceito | Por quê NÃO usar |
|----------|------------------|
| **ReAct Pattern** | Fluxo é determinístico, não precisa "pensar" |
| **Tool Calling Dinâmico** | Sempre usa Tavily, não há escolha |
| **RAG com Vector Store** | Summary já está em texto no estado |
| **Agents Autônomos** | É workflow orquestrado, não autônomo |
| **Múltiplas Ferramentas** | Tavily sozinho é suficiente |
| **LangChain Agents** | LangGraph oferece controle mais fino |

---

## 📈 Progressão de Código

### MVP 1: Funções Puras (Procedural) ✅
```python
def search_tavily(state: State) -> dict:
    """Função pura: recebe estado, retorna dict"""
    results = tavily.invoke(state["topic"])
    return {"results": results}
```

**Vantagens:** Simples, fácil de testar, sem side effects

---

### MVP 2-3: Mantém Funções Puras (adiciona interação)

### MVP 4: Opcional - Classes Leves (OOP)
```python
class HealthBotNodes:
    """Organiza nós relacionados"""
    def __init__(self, llm, tavily):
        self.llm = llm
        self.tavily = tavily
    
    def search(self, state):
        results = self.tavily.invoke(state["topic"])
        return {"results": results}
```

**Vantagens:** Reutilização, configuração centralizada

---

## ✅ Checklist de Requisitos do Projeto

### Funcionalidades Obrigatórias

- [ ] 1. Perguntar tópico de saúde ao paciente
- [x] 2. Buscar no Tavily focando em fontes médicas confiáveis
- [x] 3. Resumir resultados em linguagem acessível
- [x] 4. Apresentar resumo ao paciente
- [ ] 5. Solicitar confirmação de prontidão para quiz
- [ ] 6. Gerar 1 pergunta de quiz baseada no resumo
- [ ] 7. Apresentar a pergunta do quiz
- [ ] 8. Receber resposta do paciente
- [ ] 9. Avaliar resposta com nota + justificativa + citações
- [ ] 10. Apresentar avaliação ao paciente
- [ ] 11. Perguntar se quer novo tópico ou sair
- [ ] 12. Loop (resetar estado) ou finalizar

### Requisitos Técnicos

- [x] Usar LangGraph para workflow
- [x] Usar Tavily Community Tool do LangChain
- [x] Estado deve persistir entre nós
- [ ] Reset de estado ao iniciar novo tópico
- [x] Código organizado e profissional

**Progresso:** 5/12 funcionalidades (42%) | 4/5 requisitos técnicos (80%)

---

## 🎯 Status Atual

**MVP Atual:** ✅ **MVP 1 COMPLETO**

**Próximo Passo:** Começar MVP 2 - Human-in-the-Loop

**Bloqueadores:** Nenhum

**Conquistas:**
- ✅ Sprint 1: Configurações com busca automática do .env
- ✅ Sprint 2: Estado tipado criado
- ✅ Sprint 3: Nós implementados e testados
- ✅ Sprint 4: Grafo compilado e funcional

**Notas:** 
- Ambiente configurado ✅
- APIs configuradas e validadas ✅
- Git configurado ✅
- MVP1 testado e funcional ✅
- Resumo gerado com qualidade profissional ✅

---

## 📚 Referências Úteis

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Tavily Search API](https://docs.tavily.com/)
- [LangChain Expression Language](https://python.langchain.com/docs/expression_language/)
- [TypedDict Python](https://docs.python.org/3/library/typing.html#typing.TypedDict)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

---
