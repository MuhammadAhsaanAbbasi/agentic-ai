# # type: ignore
# from phi.playground import Playground, serve_playground_app
# from phi.assistant import Assistant
# from phi.agent import Agent
# from phi.model.openai import OpenAIChat
# from phi.storage.agent.sqlite import SqlAgentStorage
# from phi.tools.duckduckgo import DuckDuckGo
# from phi.tools.yfinance import YFinanceTools
# from dotenv import load_dotenv
# from phi.knowledge.pdf import PDFUrlKnowledgeBase
# from phi.vectordb.chroma import ChromaDb
# from phi.storage.agent.postgres import PgAgentStorage
# from phi.document.chunking.agentic import AgenticChunking
# from phi.embedder.openai import OpenAIEmbedder
# import typer
# import os
# _ = load_dotenv()

# DATABASE_URL = os.environ.get("DATABASE_URL")
# db_url = str(DATABASE_URL).replace("postgresql://", "postgresql+psycopg://")

# knowledge_base = PDFUrlKnowledgeBase(
#     urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
#     # Table name: ai.pdf_documents
#     vector_db=ChromaDb(
#         collection="recipes",
#         embedder=OpenAIEmbedder(model="text-embedding-3-small"),
#     ),
#     chunking_strategy=AgenticChunking(max_chunk_size=1000),
#     num_documents=5,
# )

# knowledge_base.load(recreate=True, upsert=True)

# storage = PgAgentStorage(
#     table_name="agent_sessions", 
#     db_url=db_url
# )

# web_agent = Agent(
#     name="Web Agent",
#     model=OpenAIChat(id="gpt-4o"),
#     tools=[DuckDuckGo()],
#     instructions=["Always include sources"],
#     markdown=True,
# )

# finance_tool = YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)

# finance_agent = Agent(
#     name="Finance Agent",
#     model=OpenAIChat(id="gpt-4o"),
#     tools=[finance_tool],
#     instructions=["Use tables to display data"],
#     markdown=True,
# )

# # Create a team of agents
# team = [web_agent, finance_agent]

# def pdf_agent(user: str = "user"):
#     run_id: Optional[str] = None

#     agent = Assistant(
#     name="Teams of Agents",
#     llm=OpenAIChat(id="gpt-4o-mini"),  # Use OpenAI's GPT-4 model
#     team=team,
#     run_id=run_id,
#     user_id=user,
#     instructions=["Always include sources", "Use tables to display data"],
#     storage=storage,
#     knowledge_base=knowledge_base,
#     read_chat_history=True,
#     search_knowledge=True,
#     show_tool_calls=True,
#     debug_mode=True,
# )
#     if run_id is None:
#         run_id = agent.run_id
#         print(f"Started Run: {run_id}\n")
#     else:
#         print(f"Continuing Run: {run_id}\n")
    
#     agent.cli_app(markdown=True)


# pdf_agent()
