from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.custom_tool import docs_scrape_tool, search_tool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class CustomerSupport():
	"""CustomerSupport crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def support_agent(self) -> Agent:
		return Agent(
			config=self.agents_config["support_agent"],
			verbose=True
		)

	@agent
	def support_quality_assurance_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['support_quality_assurance_agent'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def inquiry_resolution(self) -> Task:
		return Task(
			config=self.tasks_config['inquiry_resolution'],
			tools=[search_tool]
		)

	@task
	def quality_assurance_review(self) -> Task:
		return Task(
			config=self.tasks_config['quality_assurance_review'],
			tools=[docs_scrape_tool]
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the CustomerSupport crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
