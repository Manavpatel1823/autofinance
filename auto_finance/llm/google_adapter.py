from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from .base import BaseLLMAdapter, LLMResponse
from typing import List, Dict

class GoogleGenerativeAIAdapter(BaseLLMAdapter):
    """Adapter for Google's Generative AI"""
    
    def __init__(
        self,
        model_name: str = "gemini-pro",
        temperature: float = 0.3,
        google_api_key: str = None,
        **kwargs
    ):
        if not google_api_key:
            raise ValueError("Google API key is required")
            
        # Configure the Google Generative AI
        genai.configure(api_key=google_api_key)
        
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            google_api_key=google_api_key,
            **kwargs
        )
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        response = self.llm.invoke(messages)
        return LLMResponse(
            content=response.content,
            raw_response=response
        )
    
    def get_embedding(self, text: str) -> List[float]:
        # Implement embedding logic for Google's API
        pass