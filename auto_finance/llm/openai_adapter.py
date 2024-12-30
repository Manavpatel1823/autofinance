from openai import OpenAI
from .base import BaseLLMAdapter, LLMResponse
from typing import List, Dict

class OpenAIAdapter(BaseLLMAdapter):
    """Adapter for OpenAI's API"""
    
    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.3,
        api_key: str = None,
        **kwargs
    ):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.kwargs = kwargs
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            **{**self.kwargs, **kwargs}
        )
        return LLMResponse(
            content=response.choices[0].message.content,
            raw_response=response
        )
    
    def get_embedding(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding