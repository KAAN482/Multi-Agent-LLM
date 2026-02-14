from langchain_core.messages import HumanMessage
from src.models.ollama_model import OllamaModel
from src.config import MODEL_DEEPSEEK_CODER
from src.utils.logger import get_logger
from langchain_core.prompts import ChatPromptTemplate
from src.tools.code_executor import code_executor_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

logger = get_logger(__name__)

def logic_expert_node(state, config):
    """
    3️⃣ 🧮 DeepSeek Coder 1.3B (Tool / Logic Agent)
    
    Görevleri:
    - Matematik hesaplama
    - Python kod üretimi ve çalıştırma
    - JSON üretme
    - Mantıksal kurallar
    """
    logger.info("DeepSeek Logic Expert çalıştırılıyor")
    
    messages = state["messages"]
    last_message = messages[-1] # Genelde Llama veya Gemini'den gelir
    
    # DeepSeek Coder Modeli
    model_client = OllamaModel(model_name=MODEL_DEEPSEEK_CODER, temperature=0.0) # Kod için 0 sıcaklık
    model = model_client.llm
    
    tools = [code_executor_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen DeepSeek Coder, bu sistemin 'Mantık ve Kod Uzmanı'sın.
        Görevin:
        1. Gelen isteği python kodu yazarak veya mantıksal çıkarsama ile çözmek.
        2. 'code_executor' aracını kullanarak kodu çalıştır ve sonucu al.
        3. Sonucu net, kısa ve JSON veya yapılandırılmış formatta döndür.
        4. Yorum yapma, sadece sonucu ver.
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    response = agent_executor.invoke({"input": last_message.content, "chat_history": messages[:-1]})
    
    return {"messages": [HumanMessage(content=response["output"], name="logic_expert")]}
