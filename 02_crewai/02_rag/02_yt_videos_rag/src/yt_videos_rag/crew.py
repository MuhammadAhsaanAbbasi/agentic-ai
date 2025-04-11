from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from typing import List, Optional
from crewai_tools import RagTool, FirecrawlSearchTool
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from yt_videos_rag.model.model import ContentCreatorInfo
from yt_videos_rag.tools.FetchYTVideos import FetchLatestVideosFromYTChannel
from yt_videos_rag.tools.AddVideoVectorDBTool import AddVideoVectorDBTool
from dotenv import load_dotenv

_ = load_dotenv()

# --- Tools ---
fetch_latest_videos_tool = FetchLatestVideosFromYTChannel()
add_video_vector_db_tool = AddVideoVectorDBTool()
fire_crawl_search_tool = FirecrawlSearchTool()
rag_tool = RagTool()

@CrewBase
class YtVideosRag():
	"""02YtVideosRag crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def scrape_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['scrape_agent'],
			tools=[fetch_latest_videos_tool]
		)

	@agent
	def vector_db_agents(self) -> Agent:
		return Agent(
			config=self.agents_config['vector_db_agents'],
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

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
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
		"""Creates the 02YtVideosRag crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
