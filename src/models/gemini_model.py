import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

class GeminiModel:
    def __init__(self, model_name="gemini-2.5-flash", api_key=None, temperature=0.7):
        """
        Google Gemini model istemcisi.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY bulunamadı!")
            
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=self.api_key,
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
