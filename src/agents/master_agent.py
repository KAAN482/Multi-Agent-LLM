from langchain_core.messages import HumanMessage
from src.models.gemini_model import GeminiModel
from src.config import MODEL_GEMINI_MASTER
from src.utils.logger import get_logger
from langchain_core.prompts import ChatPromptTemplate
from src.tools.web_search import web_search_tool
from langchain.agents import AgentExecutor, create_tool_calling_agent

logger = get_logger(__name__)

async def master_agent_node(state, config):
    """
    2️⃣ 🌍 Gemini 2.5 Flash (Master & Web Agent)
    
    Görevleri:
    - Web araştırması (Eksik bilgi varsa)
    - Analist (Llama) ve Mantık (DeepSeek) çıktılarının kontrolü
    - Çelişki tespiti
    - Final output üretimi (Akademik düzenleme)
    """
    logger.info("Gemini Master Agent çalıştırılıyor")
    
    messages = state["messages"]
    
    # Mesaj geçmişini analiz et: Hangi ajanlar çalıştı?
    analyst_msg = next((m for m in reversed(messages) if m.name == "analyst"), None)
    logic_msg = next((m for m in reversed(messages) if m.name == "logic_expert"), None)
    
    # Giriş (Input) hazırlığı
    user_input = messages[0].content
    context_str = ""
    if analyst_msg:
        context_str += f"\n[ANALİST RAPORU]:\n{analyst_msg.content}\n"
    if logic_msg:
        context_str += f"\n[MANTIK UZMANI SONUCU]:\n{logic_msg.content}\n"
        
    final_input = f"Kullanıcı Sorusu: {user_input}\n\nEldeki Bağlam:{context_str}\n\nGörevin: Bu bilgileri kullanarak nihai cevabı üret."

    # Gemini Modeli
    model_client = GeminiModel(model_name=MODEL_GEMINI_MASTER, temperature=0.7)
    model = model_client.llm
    
    tools = [web_search_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen Gemini 2.5 Flash, bu sistemin 'Master Agent'ısın. En üst düzey karar vericisin.
        
        Görevlerin:
        1. Llama (Analist) ve DeepSeek (Mantık) ajanlarından gelen raporları değerlendir.
        2. Eğer raporda eksik bilgi varsa veya güncel bilgi gerekiyorsa 'web_search' aracını kullan.
        3. Ajan çıktıları arasında çelişki varsa tespit et ve doğrusunu bul.
        4. Sonucu akademik, yapılandırılmış ve detaylı bir formatta kullanıcıya sun.
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Gemini asenkron çalışabilir
    response = await agent_executor.ainvoke({"input": final_input, "chat_history": []}) # Chat history master için temiz olabilir veya özet geçilebilir
    
    return {"messages": [HumanMessage(content=response["output"], name="master")]}
