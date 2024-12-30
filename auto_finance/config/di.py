from dependency_injector import containers, providers
from auto_finance.llm.google_adapter import GoogleGenerativeAIAdapter
from auto_finance.agents.analysis_agent import StockAnalysisAgent

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    # Configure Google LLM adapter
    google_llm = providers.Singleton(
        GoogleGenerativeAIAdapter,
        google_api_key=config.google_api_key,
        temperature=config.temperature,
    )
    
    # Configure Stock Analysis Agent
    stock_analysis_agent = providers.Singleton(
        StockAnalysisAgent,
        llm_adapter=google_llm
    )