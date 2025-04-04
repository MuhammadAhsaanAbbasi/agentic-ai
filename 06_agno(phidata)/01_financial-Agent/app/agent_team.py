# type: ignore
import os
import typer
from rich.prompt import Prompt
from typing import Optional
from dotenv import load_dotenv

from phi.agent import Agent
from phi.model.openai import OpenAIChat
from phi.storage.agent.sqlite import SqlAgentStorage
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.yfinance import YFinanceTools
from phi.embedder.openai import OpenAIEmbedder
from phi.document.chunking.agentic import AgenticChunking
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.vectordb.chroma import ChromaDb
load_dotenv()

vector_db = ChromaDb(
    collection="recipes",
    embedder=OpenAIEmbedder(model="text-embedding-3-small"),
)

knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    vector_db=vector_db,
    chunking_strategy=AgenticChunking(max_chunk_size=1000),
    num_documents=5,
)

# knowledge_base.load(recreate=False)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)],
    show_tool_calls=True,
)

web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    tools=[DuckDuckGo()],
    show_tool_calls=True,
)

ragAgent = Agent(
    name="RAG Agent",
    role="Search the knowledge base for recipes",
    knowledge_base=knowledge_base,
    search_knowledge=True,
)

agent_team = Agent(
    name="Multi-Capability Team",
    team=[ragAgent, finance_agent, web_agent],
    instructions=[
        "Use the RAG Agent to retrieve recipes from the knowledge base.",
        "If you don't find the information in the knowledge base, use the Finance Agent for financial data queries.",
        "If you don't find the information in the knowledge base, use the Web Agent for general web searches.",
    ],
    knowledge_base=knowledge_base,
    show_tool_calls=True,
    markdown=True,
    debug_mode=True
)

agent_team.knowledge.load(recreate=False)
agent_team.print_response("What's the current stock price of AAPL and can you find a recipe for Thai green curry?", stream=True)