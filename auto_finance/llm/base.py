from abc import ABC, abstractmethod
from typing import List, Dict, Any

class LLMResponse:
    """Standardized response format for LLM outputs"""
    def __init__(self, content: str, raw_response: Any = None):
        self.content = content
        self.raw_response = raw_response

class BaseLLMAdapter(ABC):
    """Base adapter interface for LLM providers"""
    
    @abstractmethod
    def invoke(self, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
        """Process messages and return response"""
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text"""
        pass
