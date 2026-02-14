import operator
from typing import Annotated, Sequence, TypedDict, Union, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, END

# Yeni Ajanlar
from src.agents.ana_analist import analyst_node
from src.agents.mantik_uzmani import logic_expert_node
from src.agents.master_agent import master_agent_node
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Graph State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    next: str

# Router Mantığı (Conditional Edge)
def router_logic(state: AgentState) -> Literal["LogicExpert", "MasterAgent"]:
    """
    Analist (Llama) çıktısına göre bir sonraki adımı belirler.
    Eğer 'HESAPLAMA GEREKLİ' veya benzeri bir sinyal varsa LogicExpert'e gider.
    Yoksa doğrudan MasterAgent'a gider.
    """
    messages = state["messages"]
    last_message = messages[-1]
    content = last_message.content.upper()
    
    # Basit anahtar kelime kontrolü (Llama'nın çıktısında bu kelimeleri arıyoruz)
    # Llama prompt'unda bunu belirtmemiz lazım veya genel bir analiz yapmalıyız.
    if "HESAPLAMA" in content or "KOD" in content or "PYTHON" in content:
        logger.info("Yönlendirme: LogicExpert (Hesaplama gerekli)")
        return "LogicExpert"
    
    logger.info("Yönlendirme: MasterAgent (Doğrudan sentez)")
    return "MasterAgent"

# Graph Oluşturma
workflow = StateGraph(AgentState)

# Düğümler
workflow.add_node("Analyst", analyst_node)         # Llama 3.1
workflow.add_node("LogicExpert", logic_expert_node)# DeepSeek Coder
workflow.add_node("MasterAgent", master_agent_node)# Gemini 2.5

# Akış
# 1. Her zaman Analist ile başla
workflow.set_entry_point("Analyst")

# 2. Analist -> (Karar) -> LogicExpert veya MasterAgent
workflow.add_conditional_edges(
    "Analyst",
    router_logic,
    {
        "LogicExpert": "LogicExpert",
        "MasterAgent": "MasterAgent"
    }
)

# 3. LogicExpert -> MasterAgent
workflow.add_edge("LogicExpert", "MasterAgent")

# 4. MasterAgent -> END
workflow.add_edge("MasterAgent", END)

# Compile
graph = workflow.compile()

async def run_multi_agent(query: str, mode: str = "auto") -> dict:
    """
    Sistemi Çalıştıran Ana Fonksiyon.
    """
    from langchain_core.messages import HumanMessage
    
    inputs = {"messages": [HumanMessage(content=query)]}
    
    try:
        result = await graph.ainvoke(inputs)
        
        # Son mesaj MasterAgent'tan gelir
        final_message = result["messages"][-1]
        
        # İstatistikler (Basitçe mesaj sayısı üzerinden iterasyon tahmini)
        return {
            "answer": final_message.content,
            "iterations": len(result["messages"]),
            "models_used": ["Llama 3.1", "DeepSeek Coder", "Gemini 2.5"],
            "tools_called": ["RAG", "Code Executor", "Web Search"]
        }
    except Exception as e:
        logger.error(f"Graph hatası: {e}")
        return {"answer": f"Sistem hatası: {str(e)}", "iterations": 0}

async def stream_multi_agent(query: str, mode: str = "auto"):
    """
    Sistemi Streaming (Akış) Modunda Çalıştırır.
    Her adımda (node) olay fırlatır.
    """
    from langchain_core.messages import HumanMessage
    
    inputs = {"messages": [HumanMessage(content=query)]}
    
    try:
        # astream, her node çalıştıktan sonra çıktı verir
        async for event in graph.astream(inputs, stream_mode="updates"):
            for node_name, node_output in event.items():
                # node_name: "Analyst", "LogicExpert", "MasterAgent"
                # node_output: {"messages": [...]}
                
                last_message = node_output["messages"][-1]
                content = last_message.content
                
                yield {
                    "event": "node_update",
                    "node": node_name,
                    "content": content
                }
                
                # Eğer son node MasterAgent ise, işlemi bitmiş sayabiliriz (veya graph yapısına göre END)
                if node_name == "MasterAgent":
                    yield {
                        "event": "final_result",
                        "content": content
                    }
                    
    except Exception as e:
        logger.error(f"Stream hatası: {e}")
        yield {
            "event": "error",
            "content": str(e)
        }
