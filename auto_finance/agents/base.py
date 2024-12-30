from typing import Any, Optional, List
from langchain.tools import BaseTool
from abc import ABC, abstractmethod
from auto_finance.llm.base import BaseLLMAdapter

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(
        self,
        llm_adapter: BaseLLMAdapter,
        tools: Optional[List[BaseTool]] = None
    ):
        """
        Initialize the base agent
        
        Args:
            llm_adapter: LLM adapter instance
            tools: List of tools available to the agent
        """
        self.llm = llm_adapter
        self.tools = tools or []
        
    def add_tool(self, tool: BaseTool) -> None:
        """Add a new tool to the agent's toolkit"""
        self.tools.append(tool)
        
    def remove_tool(self, tool_name: str) -> None:
        """Remove a tool from the agent's toolkit"""
        self.tools = [tool for tool in self.tools if tool.name != tool_name]
        
    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Execute the agent's main functionality"""
        pass
    
    def _format_tool_description(self) -> str:
        """Format the list of available tools for the prompt"""
        tool_descriptions = []
        for tool in self.tools:
            tool_descriptions.append(f"- {tool.name}: {tool.description}")
        return "\n".join(tool_descriptions)