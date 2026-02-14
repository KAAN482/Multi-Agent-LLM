import os
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

class OllamaModel:
    def __init__(self, model_name="llama3.2:3b", base_url="http://localhost:11434", temperature=0.7):
        """
        Ollama yerel model istemcisi.
        """
        self.model_name = model_name
        self.base_url = base_url
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=temperature
        )

    def generate(self, prompt: str, system_prompt: str = None) -> str:
        """
        Tek seferlik üretim yapar.
        """
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=prompt))
        
        response = self.llm.invoke(messages)
        return response.content
