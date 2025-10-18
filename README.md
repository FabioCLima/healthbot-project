# 🏥 HealthBot Project

AI-powered Patient Education System using LangGraph and LangChain

Mostrar Imagem
Mostrar Imagem
Mostrar Imagem

📋 Sobre o Projeto
O HealthBot é um sistema de educação para pacientes que utiliza Inteligência Artificial para:

🔍 Buscar informações médicas confiáveis na internet
📄 Resumir conteúdo em linguagem acessível
📝 Criar quizzes para validar compreensão
🎯 Avaliar respostas com feedback educacional
Tecnologias:

LangGraph - Orquestração de workflows com IA
LangChain - Framework para aplicações com LLMs
OpenAI GPT-4o-mini - Geração de resumos e avaliações
Tavily - Busca inteligente focada em fontes confiáveis
🚀 Quick Start
Pré-requisitos
Python 3.13+
API Keys: OpenAI e Tavily
Instalação
cd healthbot-project

## Crie e ative o ambiente virtual

python -m venv .venv
source .venv/bin/activate  # Linux/Mac

## ou

.venv\Scripts\activate     # Windows

## Instale as dependências

pip install -e .
Configuração
Crie um arquivo .env na raiz do projeto:
TAVILY_API_KEY=tvly-...

## LangSmith (opcional - para debug)

LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_PROJECT=HealthBot Prototype
Teste a configuração
bash
python src/healthbot/test_configurations.py
Execute o MVP1
bash
python src/healthbot/test_graph.py
📊 Status do Desenvolvimento
MVP 1: Sequential Chain ✅ COMPLETO
Fluxo linear básico com busca e resumo

[START] → [set_topic] → [search_tavily] → [summarize] → [print_summary] → [END]
Features implementadas:

✅ Busca automática de informações médicas no Tavily
✅ Resumo em linguagem acessível com OpenAI
✅ Estado tipado (TypedDict)
✅ Configurações com busca automática do .env
✅ Testes unitários para cada componente
Exemplo de saída:

Topic: diabetes
Results: 3318 caracteres de 3 fontes confiáveis
Summary: 1376 caracteres - resumo educacional profissional
MVP 2: Human-in-the-Loop ⬜ PRÓXIMO
Adicionar interação com usuário

⬜ Perguntar tópico ao usuário
⬜ Aguardar confirmação antes de continuar
⬜ Sistema de mensagens (chat)
⬜ Checkpointer para persistência
MVP 3: Sistema de Quiz ⬜ PENDENTE
Geração e avaliação de quiz

⬜ Gerar pergunta baseada no resumo
⬜ Receber resposta do paciente
⬜ Avaliar com nota e feedback
⬜ Citações do resumo na avaliação
MVP 4: Loop e Decisões ⬜ PENDENTE
Fluxo completo com repetição

⬜ Perguntar se quer novo tópico
⬜ Conditional routing
⬜ Reset de estado
⬜ Finalização
Progresso geral: 25% (1/4 MVPs)

🏗️ Arquitetura
Estrutura do Projeto
healthbot-project/
├── .env                        # Variáveis de ambiente (não commitar!)
├── pyproject.toml              # Configuração do projeto
├── README.md                   # Este arquivo
├── mvp_architecture_doc_health_bot.md  # Documentação técnica detalhada
│
├── src/
│   └── healthbot/
│       ├── __init__.py
│       ├── settings.py         # Configurações e validação de API keys
│       ├── state.py            # Definição do Estado (TypedDict)
│       ├── nodes.py            # Nós do grafo (funções)
│       ├── graph.py            # Construção do grafo LangGraph
│       ├── main.py             # Ponto de entrada (futuro)
│       │
│       └── [testes]
│           ├── test_configurations.py
│           ├── test_state.py
│           ├── test_nodes_simple.py
│           └── test_graph.py
│
└── tests/                      # Testes com pytest (futuro)
    └── __init__.py
Padrões de Design
Sequential Chain Pattern - Fluxo linear de transformações
Human-in-the-Loop Pattern - Pausas para input do usuário
Conditional Router Pattern - Decisões que alteram o fluxo
Stateful Workflow Pattern - Estado compartilhado entre nós

## 🧪 Testes

### Teste do estado

python src/healthbot/test_state.py

### Teste dos nós

python src/healthbot/test_nodes_simple.py

### Teste do grafo completo (MVP1)

python src/healthbot/test_graph.py
📚 Documentação
Para documentação técnica detalhada, incluindo:

Análise de padrões de design
Arquitetura de cada MVP
Exemplos de código
Conceitos de LangGraph
Consulte: mvp_architecture_doc_health_bot.md

🛠️ Desenvolvimento
Tecnologias Utilizadas
Biblioteca	Versão	Propósito
langchain	0.2.16+	Framework para LLMs
langchain-openai	0.1.23+	Integração OpenAI
langgraph	0.2.19+	Orquestração de workflows
tavily-python	0.4.0+	Busca inteligente
pydantic	2.7+	Validação de dados
python-dotenv	1.0.1+	Gerenciamento de .env
Linting e Formatação
bash
# Verificar código
ruff check .

# Formatar código

ruff format .

## Corrigir automaticamente

ruff check . --fix
🎯 Roadmap
 Sprint 1: Configurações e validação de API keys
 Sprint 2: Estado tipado (TypedDict)
 Sprint 3: Nós do grafo (funções puras)
 Sprint 4: Grafo compilado e funcional (MVP1)
 Sprint 5: Interação com usuário (MVP2)
 Sprint 6: Sistema de quiz (MVP3)
 Sprint 7: Loop condicional (MVP4)
 Sprint 8: Testes e refinamentos
 Sprint 9: Documentação final
 Sprint 10: Submissão
Deadline: 29/10/2025

📝 Requisitos do Projeto
Funcionalidades Obrigatórias
 Perguntar tópico de saúde ao paciente
 Buscar no Tavily focando em fontes médicas confiáveis
 Resumir resultados em linguagem acessível
 Apresentar resumo ao paciente
 Solicitar confirmação de prontidão para quiz
 Gerar 1 pergunta de quiz baseada no resumo
 Apresentar a pergunta do quiz
 Receber resposta do paciente
 Avaliar resposta com nota + justificativa + citações
 Apresentar avaliação ao paciente
 Perguntar se quer novo tópico ou sair
 Loop (resetar estado) ou finalizar
Progresso: 4/12 (33%)

👤 Autor
Fabio Lima

Email: lima.fisico@gmail.com
GitHub: @FabioCLima
📄 Licença
Este é um projeto educacional desenvolvido como parte do curso de LangGraph e LangChain.

🙏 Agradecimentos
Udacity - Curso de LangGraph/LangChain
LangChain - Framework e documentação
OpenAI - Modelos GPT
Tavily - API de busca
Última atualização: 18/10/2025 - MVP1 Completo ✅