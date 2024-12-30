from anthropic import Anthropic
from .base import BaseLLMAdapter, LLMResponse
from typing import List, Dict

class AnthropicAdapter(BaseLLMAdapter):
    """Adapter for Anthropic's API"""
    
    def __init__(
        self,
        model_name: str = "claude-3-opus-20240229",
        temperature: float = 0.3,
        api_key: str = None,
        **kwargs
    ):
        self.client = Anthropic(api_key=api_key)
        self.model_name = model_name
        self.temperature = temperature
        self.kwargs = kwargs
    
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        response = self.client.messages.create(
            model=self.model_name,
            messages=messages,
            temperature=self.temperature,
            **{**self.kwargs, **kwargs}
        )
        return LLMResponse(
            content=response.content[0].text,
            raw_response=response
        )
    
    def get_embedding(self, text: str) -> List[float]:
        # Implement when Anthropic releases embedding model
        pass