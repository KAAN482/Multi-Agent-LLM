from langchain_core.messages import HumanMessage
from src.models.ollama_model import OllamaModel
from src.config import MODEL_DEEPSEEK_CODER
from src.utils.logger import get_logger
from src.tools.code_executor import code_executor_tool
from langgraph.prebuilt import create_react_agent

logger = get_logger(__name__)

def logic_expert_node(state, config):
    """
    3️⃣ 🧮 DeepSeek Coder 1.3B (Tool / Logic Agent)
    """
    logger.info("DeepSeek Logic Expert çalıştırılıyor")
    
    messages = state["messages"]
    
    # DeepSeek Coder Modeli (Sıcaklık 0)
    model_client = OllamaModel(model_name=MODEL_DEEPSEEK_CODER, temperature=0.0)
    model = model_client.llm
    
    tools = [code_executor_tool]
    
    system_prompt = """Sen DeepSeek Coder, bu sistemin 'Mantık ve Kod Uzmanı'sın.
    Görevin:
    1. Gelen isteği python kodu yazarak veya mantıksal çıkarsama ile çözmek.
    2. 'code_executor' aracını kullanarak kodu çalıştır ve sonucu al.
    3. Sonucu net, kısa ve JSON veya yapılandırılmış formatta döndür.
    4. Yorum yapma, sadece sonucu ver.
    """
    
    # create_react_agent (Senkron invoke için)
    agent = create_react_agent(model, tools, state_modifier=system_prompt)
    
    response = agent.invoke({"messages": messages})
    
    final_message = response["messages"][-1]
    
    return {"messages": [HumanMessage(content=final_message.content, name="logic_expert")]}
