from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from ai_news_letter.tools.custom_tool import search_tool, scrape_tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

_ = load_dotenv()

manager_llm = ChatOpenAI(model="gpt-4o-mini")

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AiNewsLetter():
	"""AiNewsLetter crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def news_topic_researcher_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['news_topic_researcher_agent'],
			tools=[search_tool],
			verbose=True
		)

	@agent
	def news_fetcher_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['news_fetcher_agent'],
			tools=[search_tool, scrape_tool],
			verbose=True
		)
	
	@agent
	def news_analyzer_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['news_analyzer_agent'],
			tools=[search_tool, scrape_tool],
			verbose=True
		)

	@agent
	def news_editor_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['news_editor_agent'],
			verbose=True
		)
	
	@agent
	def news_compiler_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['news_compiler_agent'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def news_topic_research_task(self) -> Task:
		return Task(
			config=self.tasks_config['news_topic_research_task'],
		)

	@task
	def news_fetch_task(self) -> Task:
		return Task(
			config=self.tasks_config['news_fetch_task'],
		)
	
	@task
	def news_analyzed_task(self) -> Task:
		return Task(
			config=self.tasks_config['news_analyzed_task'],
		)
	
	@task
	def news_edit_task(self) -> Task:
		return Task(
			config=self.tasks_config['news_edit_task'],
		)
	
	@task
	def news_compile_task(self) -> Task:
		return Task(
			config=self.tasks_config['news_compile_task'],
			output_file='today_news.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AiNewsLetter crew"""
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
