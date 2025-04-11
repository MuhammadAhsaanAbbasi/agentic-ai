from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Optional
from crewai_tools import RagTool, FirecrawlSearchTool
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from yt_videos_rag.model.model import ContentCreatorInfo
from yt_videos_rag.tools.FetchYTVideos import FetchLatestVideosFromYTChannel
from yt_videos_rag.tools.AddVideoVectorDBTool import AddVideoVectorDBTool
from crewai_tools.tools.firecrawl_search_tool.firecrawl_search_tool import FirecrawlSearchTool
from crewai_tools.tools.firecrawl_search_tool.firecrawl_search_tool import FirecrawlApp
import os

# Load environment variables
_ = load_dotenv()

# --- Tools ---
fetch_latest_videos_tool = FetchLatestVideosFromYTChannel()
add_video_vector_db_tool = AddVideoVectorDBTool()
# Instead of instantiating FirecrawlApp directly, use FirecrawlSearchTool:

class PatchedFirecrawlSearchTool(FirecrawlSearchTool):
    def _initialize_firecrawl(self):
        self._firecrawl = FirecrawlApp(api_key=self.api_key)

# Then use the patched tool:
fire_crawl_search_tool = PatchedFirecrawlSearchTool(api_key=os.getenv("FIRECRAWL_API_KEY"))

rag_tool = RagTool()

@CrewBase
class YtVideosRag():
    """02YtVideosRag crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def scrape_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['scrape_agent'],
            tools=[fetch_latest_videos_tool]
        )

    @agent
    def vector_db_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['vector_db_agent'],
            tools=[add_video_vector_db_tool]
        )
    
    @agent
    def general_research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['general_research_agent'],
            tools=[rag_tool]
        )
    
    @agent
    def follow_up_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['follow_up_agent'],
            tools=[rag_tool]
        )
    
    @agent
    def fallback_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['fallback_agent'],
            tools=[fire_crawl_search_tool]
        )

    @task
    def scrape_youtube_channel(self) -> Task:
        return Task(
            config=self.tasks_config['scrape_youtube_channel'],
        )

    @task
    def process_videos_task(self) -> Task:
        return Task(
            config=self.tasks_config['process_videos_task'],
        )
    
    @task
    def find_initial_information_task(self) -> Task:
        return Task(
            config=self.tasks_config['find_initial_information_task'],
            tools=[rag_tool],
            output_pydantic=ContentCreatorInfo
        )
    
    @task
    def follow_up_task(self) -> Task:
        return Task(
            config=self.tasks_config['follow_up_task'],
            tools=[rag_tool],
            output_pydantic=ContentCreatorInfo
        )
    
    @task
    def fallback_task(self) -> Task:
        return Task(
            config=self.tasks_config['fallback_task'],
            tools=[fire_crawl_search_tool],
            output_pydantic=ContentCreatorInfo,
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents, 
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
