from agents import ( 
    Agent, 
    # OpenAIChatCompletionsModel, AsyncOpenAI, 
    Runner, function_tool
)
from duckduckgo_search import DDGS
from dotenv import load_dotenv
from datetime import datetime
_ = load_dotenv()

current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
model="o3-mini-2025-01-31"

@function_tool
def search(topic: str):
    """Search the web for the given topic."""
    with DDGS() as ddgs:
        return [result for result in ddgs.text(f"{topic}/ {current_time}", max_results=5)]

news_agent = Agent(
    name="News Assistant",
    instructions="YOu Provide the latest news articles for a given topic using DuckDuckgoSearch Tools.",
    tools=[search],
    model=model
)

editor_agent = Agent(
    name="Editor Assistant",
    instructions="You are an editor and you are responsible for editing the news articles.",
    model=model
)

def run_news_workflow(topic: str):
    news = Runner.run_sync(news_agent, topic)
    edited_news_response = Runner.run_sync(editor_agent, news.final_output)
    edited_news = edited_news_response.final_output
    print("Final News Articles:")
    print(edited_news)
    return edited_news

response  = run_news_workflow("AI")

print(response)