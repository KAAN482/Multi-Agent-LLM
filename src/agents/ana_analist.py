from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from src.tools.rag_tool import rag_tool
from src.utils.logger import get_logger
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.models.ollama_model import OllamaModel
from src.config import MODEL_LLAMA_ANALYZER

logger = get_logger(__name__)

async def analyst_node(state, config):
    """
    1️⃣ 🦙 Llama 3.1 (Analist & RAG Uzmanı)
    
    Görevleri:
    - Kullanıcı sorgu analizi
    - RAG context birleştirme
    - Doküman + tablo yorumlama
    - İlk reasoning
    - Gemini’ye gidecek prompt’u hazırlama
    """
    logger.info("Llama Analist (Analyst) çalıştırılıyor")
    
    messages = state["messages"]
    last_message = messages[-1]
    
    # Llama 3.1 Modelini Yükle
    model_client = OllamaModel(model_name=MODEL_LLAMA_ANALYZER, temperature=0.1) # Analiz için düşük sıcaklık
    model = model_client.llm
    
    tools = [rag_tool]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """Sen Llama 3.1, bu sistemin 'Analist ve RAG Uzmanı'sın.
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
        """),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(model, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    # Asenkron çağrı
    response = await agent_executor.ainvoke({"input": last_message.content, "chat_history": messages[:-1]})
    
    return {"messages": [HumanMessage(content=response["output"], name="analyst")]}
