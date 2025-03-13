from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from langchain_community.tools.human.tool import HumanInputRun
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from youtube_automation_crew.tools.youtube_video_detail_tool import YouTubeVideoDetailsTool
from youtube_automation_crew.tools.youtube_search_tool import YoutubeVideoSearchTool
import os

youtube_video_search_tool = YoutubeVideoSearchTool()
youtube_video_details_tool = YouTubeVideoDetailsTool()

from crewai.tools import BaseTool
from langchain_community.tools.human.tool import HumanInputRun

class MyCustomHumanTool(BaseTool):
    name: str = "Human Input Tool"
    description: str = "Ask a human for guidance when stuck."
    
    def _run(self, query: str) -> str:
        # Instantiate the native human tool and invoke it with the query.
        human_tool = HumanInputRun()
        response = human_tool.invoke(query)
        return response



_ = load_dotenv()
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-rew-class-with-decorators

model = os.getenv("MODEL")
api_key=os.getenv("GEMINI_API_KEY")
openai_api_key=os.getenv("OPENAI_API_KEY")
manager_llm = ChatOpenAI(model="o3-mini-2025-01-31", api_key=openai_api_key) 

llm = LLM(model=model, api_key=api_key)

@CrewBase
class YoutubeAutomationCrew():
	"""YoutubeAutomationCrew crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tool

	@agent
	def youtube_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['youtube_researcher'],
			llm=llm,
			tools=[youtube_video_search_tool, youtube_video_details_tool]
		)
	
	@agent
	def title_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['title_creator'],
			llm=llm,
		)
	
	@agent
	def description_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['description_creator'],
			llm=llm,
		)
	
	@agent
	def email_creator(self) -> Agent:
		return Agent(
			config=self.agents_config['email_creator'],
			llm=llm,
			tools=[MyCustomHumanTool()]
		)
	
	@agent
	def youtube_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['youtube_manager'],
			llm=llm,
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def youtube_video_research(self) -> Task:
		return Task(
			config=self.tasks_config['youtube_video_research'],
		)

	@task
	def create_youtube_video_title(self) -> Task:
		return Task(
			config=self.tasks_config['create_youtube_video_title'],
		)
	
	@task
	def create_youtube_video_description(self) -> Task:
		return Task(
			config=self.tasks_config['create_youtube_video_description'],
		)
	
	@task
	def create_email_announcement(self) -> Task:
		return Task(
			config=self.tasks_config['create_email_announcement'],
		)
	
	@task
	def manage_youtube_video_creation(self) -> Task:
		return Task(
			config=self.tasks_config['manage_youtube_video_creation'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the YoutubeAutomationCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.hierarchical,
			manager_llm=manager_llm,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
