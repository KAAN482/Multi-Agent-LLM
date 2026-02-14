from langchain_core.messages import HumanMessage
from src.models.ollama_model import OllamaModel
from src.tools.rag_tool import rag_tool
from src.utils.logger import get_logger
from langgraph.prebuilt import create_react_agent
from src.config import MODEL_LLAMA_ANALYZER

logger = get_logger(__name__)

async def analyst_node(state, config):
    """
    1️⃣ 🦙 Llama 3.1 (Analist & RAG Uzmanı)
    """
    logger.info("Llama Analist (Analyst) çalıştırılıyor")
    
    messages = state["messages"]
    
    # Llama 3.1 Modelini Yükle
    model_client = OllamaModel(model_name=MODEL_LLAMA_ANALYZER, temperature=0.1)
    model = model_client.llm
    
    tools = [rag_tool]
    
    system_prompt = """Sen Llama 3.1, bu sistemin 'Analist ve RAG Uzmanı'sın.
    Görevin:
    1. Kullanıcı sorgusunu analiz et.
    2. RAG tool'unu kullanarak dokümanlardan ilgili bilgileri çek.
    3. Çektiğin bilgileri (Context) birleştir ve yorumla.
    4. Eğer matematiksel hesaplama veya kod gerekiyorsa bunu belirt.
    5. Sonraki aşama için Gemini'ye (Master) hitaben net, yapılandırılmış bir rapor hazırla.
    
    Çıktın şunları içermelidir:
    - **BULGULAR:** Dokümanlardan elde edilen veriler.
    - **ANALİZ:** Bu verilerin yorumu.
    - **GEREKSİNİMLER:** (Varsa) Hesaplama veya ek araştırma ihtiyacı.
    - **GEMINI İÇİN PROMPT:** Gemini'nin son cevabı üretmesi için talimat.
    """
    
    # LangGraph create_react_agent kullanımı
    agent = create_react_agent(model, tools, state_modifier=system_prompt)
    
    # "messages" key'ini kullanarak invoke ediyoruz
    # create_react_agent, input olarak {"messages": ...} bekler
    response = await agent.ainvoke({"messages": messages})
    
    # Son mesajı al (AIMessage)
    final_message = response["messages"][-1]
    
    # HumanMessage olarak sarmalayıp döndürüyoruz ki Graph akışında 'analyst' olarak görünsün
    return {"messages": [HumanMessage(content=final_message.content, name="analyst")]}
