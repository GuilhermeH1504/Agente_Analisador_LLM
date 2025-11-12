
from langchain_community.document_loaders import PyPDFLoader # Importa a classe para carregar documentos PDF (parte do LangChain)
from langgraph.graph import StateGraph , START, END # Importa as classes principais para construir o grafo de estado e os nós de início/fim
from langgraph.graph.message import add_messages # Importa o utilitário para adicionar mensagens ao histórico de forma segura no LangGraph
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage, BaseMessage # Importa os tipos de mensagens (Sistema, AI, Humano, Base)
from typing import TypedDict, Annotated, Sequence, List, Union # Importa tipagens do Python para definir estruturas de dados e anotações
from langchain_core.tools import tool # Importa o decorador 'tool' do LangChain para criar funções que o LLM pode chamar
from langchain_core.tools import BaseTool # Importa a classe base para tipagem de ferramentas
import os # Importa o módulo para interagir com o sistema operacional (caminhos de arquivo)
import json # Importa o módulo JSON para serialização e desserialização (essencial para tratar argumentos das Tools)

from langchain_core.messages import ToolMessage

# Para usar o modelo OpenAI via LangChain
from langchain_groq import ChatGroq # Importa a classe específica para usar o Groq via LangChain
from dotenv import load_dotenv # Importa para carregar variáveis de ambiente (GROQ_API_KEY)

load_dotenv() # Carrega as variáveis de ambiente do arquivo .env


PASTA_CURRICULOS = 'C:\\Users\\Windows\\Documents\\pasta_curriculos' 


# DEFINIÇÃO DE ESTADO DO AGENTE (TypedDict)

class AgentState(TypedDict):
    """
    Define a estrutura de dados (estado) que será passada entre os nós do grafo.
    """
    # Define o histórico de mensagens. 'add_messages' garante que novas mensagens sejam anexadas.
    # Annotated[..., operator.add] é a forma do LangGraph de dizer: combine o novo valor com o anterior.
    messages: Annotated[Sequence[BaseMessage], add_messages]
    # Lista para armazenar o conteúdo de texto dos currículos.
    carregar: List[str] 
    # Flag booleana para indicar se a ferramenta 'carregar_pdf' já foi executada.
    data_loaded: bool 


# FERRAMENTA (TOOL)

@tool
def carregar_pdf(path: str = PASTA_CURRICULOS) -> str:
    """Carrega todos os textos de currículos em formato PDF de uma pasta específica."""
    try:
        # Lista todos os arquivos na pasta que terminam com ".pdf"
        
        file_pdf = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".pdf")]
        textos_curriculos = [] # Lista para armazenar o conteúdo de texto dos PDFs
        
        # Verifica se encontrou algum arquivo PDF
        if not file_pdf:
            return f"❌ Erro: Nenhum arquivo PDF encontrado na pasta: {path}"

        # Itera sobre cada arquivo PDF encontrado
        for file in file_pdf:
            loader = PyPDFLoader(file) # Inicializa o carregador de PDF
            pages = loader.load() # Carrega o conteúdo do PDF, retornando uma lista de Documentos
            # Concatena o conteúdo de todas as páginas em uma única string por currículo
            texto_curriculo = "\n".join([p.page_content for p in pages])
            textos_curriculos.append(texto_curriculo) # Adiciona o texto do currículo à lista
            
        # Definindo o separador claro entre os currículos para o LLM
        separator = "\n--- NOVO CURRÍCULO ---\n"
        # Convertendo a lista de currículos em uma única string
        full_text = separator.join(textos_curriculos)
        
        # Retorna a string de observação que será passada ao LLM
        return f"✅ Documentos carregados com sucesso. Total de {len(textos_curriculos)} currículos. Conteúdo a ser analisado: \n{full_text}"

    except FileNotFoundError:
        return f"❌ Erro: O caminho da pasta '{path}' não foi encontrado. Verifique o caminho."
    except Exception as e:
        return f"❌ Erro ao carregar PDFs: {e}"


# NÓ: LLM AGENTE (Decisor e Analisador)

def executar_llm(state: AgentState) -> AgentState:
    """
    Nó principal: Chama o LLM para analisar, responder ou gerar uma Tool Call.
    """
    model_name = "openai/gpt-oss-20b" # Define o nome do modelo Groq
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    # Inicializa o LLM e liga a ferramenta 'carregar_pdf' a ele
    
    llm = ChatGroq(model=model_name, groq_api_key=groq_api_key, temperature=0.3).bind_tools([carregar_pdf]) 

    # Mensagem de sistema que define o papel e a tarefa do LLM
    SYSTEM_MESSAGE = SystemMessage(
        "Você é um especialista em análise de currículos e um assistente de recrutamento. "
        "Seu trabalho é analisar os currículos fornecidos, um por um. Estamos em busca de um programador "
        "com base sólida em LLMs e Python. "
        "Para cada currículo, forneça uma análise detalhada, incluindo:\n"
        "1. Pontos Fortes (ligados a LLMs/Python).\n"
        "2. Pontos Fracos/Áreas de Oportunidade.\n"
        "3. Recomendação de Contratação (Sim/Não/Talvez).\n"
        "Use a ferramenta 'carregar_pdf' apenas se a última mensagem do usuário indicar que é hora de carregar/analisar os dados."
    )
    
    
    messages_to_llm = [SYSTEM_MESSAGE] + state["messages"] 
    
    llm_result = llm.invoke(messages_to_llm) # Invoca o LLM com o histórico e as ferramentas
    
    # Retornando o estado atualizado com a nova mensagem gerada pelo LLM.
    return {
        "messages": [llm_result] # Adicionando a resposta (ou a Tool Call) do LLM ao histórico
    }


# NÓ: EXECUTOR DE FERRAMENTAS (TOOL CALLING)

def executa_tool(state: AgentState) -> AgentState:
    """
    Nó que executa a Tool Call (chamada de função) gerada pelo LLM e devolve o resultado.
    """
    tool_call_message = state["messages"][-1] # Pega a última mensagem (deve ser a Tool Call do LLM)
    tool_calls = tool_call_message.additional_kwargs.get("tool_calls", []) # Extrai as chamadas de ferramenta
    
    if not tool_calls:
        return state 

    tool_call = tool_calls[0] # Pega a primeira Tool Call
    func_name = tool_call["function"]["name"] # Nome da função a ser executada
    raw_args = tool_call["function"]["arguments"] # Argumentos da função (pode ser string JSON ou dict)
    tool_call_id = tool_call["id"] # ID da chamada 

    
    try:
        if isinstance(raw_args, str):
            
            func_args = json.loads(raw_args)
        else:
            
            func_args = raw_args
            
    except json.JSONDecodeError:
        
        return {"messages": [AIMessage(
            content="Erro na Tool: O LLM gerou argumentos JSON inválidos para a função.", 
        )]}
        
    
    if func_name == carregar_pdf.name:
        # Executa a tool: **func_args desempacota o dicionário de argumentos para a função.
        observation = carregar_pdf.invoke(func_args) 
        
        # Criando a mensagem de observação para ser devolvida ao LLM
        tool_messages_to_add = [
            ToolMessage( # Usa ToolMessage
                content=observation, 
                name=func_name, 
                tool_call_id=tool_call_id # Liga a observação à chamada original do LLM
            )
        ]
        
        # Retorna a atualização de estado: adiciona a ToolMessage e atualiza a flag
        return {
            "messages": tool_messages_to_add,
            "data_loaded": True
        }
    
    return state # Retorna o estado se a tool não for reconhecida


# ROTEAMENTO CONDICIONAL

def roteador(state: AgentState) -> str:
    """
    Função de roteamento: Decide o próximo passo no grafo com base na saída do LLM.
    """
    last_message = state["messages"][-1] # Pega a última mensagem gerada pelo nó 'executar_llm'
    
    # Verificando se a última mensagem contém uma chamada de ferramenta
    if last_message.additional_kwargs.get("tool_calls"):
        return "tool_node" # Se sim, vai para o nó que executa a ferramenta
        
    # Se não houver tool call, o LLM gerou a resposta final
    return END # Termina a execução do grafo



# CONSTRUÇÃO DO GRAFO (LANGGRAPH)

builder = StateGraph(AgentState) # Criando o objeto construtor do grafo com o tipo de estado definido

# Adicionando os nodes
builder.add_node("executar_llm", executar_llm) # Nó principal (LLM)
builder.add_node("tool_node", executa_tool) # Nó executor de Tools

# Definindo o ponto de entrada. O processo sempre começa com o LLM para decidir a ação.
builder.set_entry_point("executar_llm") 

# Define a transição condicional que parte do LLM
builder.add_conditional_edges(
    "executar_llm", # O nó de origem
    roteador, # A função que decide o caminho (usa a Tool ou termina)
    {
        "tool_node": "tool_node", # Se o roteador retornar "tool_node", vai para o nó de execução
        END: END# Se retornar END, o grafo termina
    }
)

# Define a aresta de retorno: após executar a Tool, o resultado volta para o LLM
# O LLM lerá a ToolMessage (observação) e gerará a resposta final
builder.add_edge("tool_node", "executar_llm") 

# Compilar Grafo
graph = builder.compile() # Compilação do grafo
# graph.get_graph().draw_mermaid_png(output_file_path="ark.png") # Comando para gerar o diagrama visual do grafo


# LOOP DE INTERAÇÃO (EXECUÇÃO)

print("✅ Agente de Análise de Currículos Iniciado.")
print(f"📁 Pasta de Curriculos: {PASTA_CURRICULOS}")
print("---")

# Loop de interação com o usuário
while True:
    user_input = input("👤 Você: ") # Solicita a entrada do usuário
    
    # Verifica a condição de saída
    if user_input.lower() in ['q', 'sair']: 
        print("Até mais!")
        break
        
    
    initial_state = {"messages": [HumanMessage(content=user_input)]}

    # Invocando o grafo com o estado inicial
 
    result = graph.invoke(initial_state) 
    
    # Imprime o separador
    print("-" * 20) 
    
    # Imprime a última mensagem de conteúdo gerada pelo LLM (a resposta final)
    final_answer = result['messages'][-1].content
    print(f"🤖 AI: {final_answer}")
