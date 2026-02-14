from langchain_core.messages import HumanMessage
from src.models.gemini_model import GeminiModel
from src.config import MODEL_GEMINI_MASTER
from src.utils.logger import get_logger
from src.tools.web_search import web_search_tool
from langgraph.prebuilt import create_react_agent

logger = get_logger(__name__)

async def master_agent_node(state, config):
    """
    2️⃣ 🌍 Gemini 2.5 Flash (Master & Web Agent)
    """
    logger.info("Gemini Master Agent çalıştırılıyor")
    
    messages = state["messages"]
    
    # Mesaj geçmişini analiz et (Manuel context hazırlığı)
    analyst_msg = next((m for m in reversed(messages) if m.name == "analyst"), None)
    logic_msg = next((m for m in reversed(messages) if m.name == "logic_expert"), None)
    
    # Giriş (Input) hazırlığı
    original_user_msg = messages[0]
    user_input = original_user_msg.content
    
    context_str = ""
    if analyst_msg:
        context_str += f"\n[ANALİST RAPORU]:\n{analyst_msg.content}\n"
    if logic_msg:
        context_str += f"\n[MANTIK UZMANI SONUCU]:\n{logic_msg.content}\n"
        
    final_query = f"Kullanıcı Sorusu: {user_input}\n\nEldeki Bağlam:{context_str}\n\nGörevin: Bu bilgileri kullanarak nihai cevabı üret."

    # Gemini Modeli
    model_client = GeminiModel(model_name=MODEL_GEMINI_MASTER, temperature=0.7)
    model = model_client.llm
    
    tools = [web_search_tool]
    
    system_prompt = """Sen Gemini 2.5 Flash, bu sistemin 'Master Agent'ısın. En üst düzey karar vericisin.
    
    Görevlerin:
    1. Llama (Analist) ve DeepSeek (Mantık) ajanlarından gelen raporları değerlendir.
    2. Eğer raporda eksik bilgi varsa veya güncel bilgi gerekiyorsa 'web_search' aracını kullan.
    3. Ajan çıktıları arasında çelişki varsa tespit et ve doğrusunu bul.
    4. Sonucu akademik, yapılandırılmış ve detaylı bir formatta kullanıcıya sun.
    """
    
    agent = create_react_agent(model, tools, state_modifier=system_prompt)
    
    # Master için yeni bir mesaj dizisi oluşturuyoruz.
    # Sadece final_query'i gönderiyoruz çünkü context zaten içinde.
    # (Chat history'yi olduğu gibi verirsek model kafası karışabilir, summary yeterli)
    master_messages = [HumanMessage(content=final_query)]
    
    response = await agent.ainvoke({"messages": master_messages})
    
    final_message = response["messages"][-1]
    
    return {"messages": [HumanMessage(content=final_message.content, name="master")]}
