from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.custom_tool import search_tool, sentiment_analysis_tool, file_read_tool, directory_read_tool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class CustomerOutreach():
	"""CustomerOutreach crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def sales_rep_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['sales_rep_agent'],
			verbose=True
		)

	@agent
	def lead_sales_rep_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['lead_sales_rep_agent'],
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def lead_profiling_task(self) -> Task:
		return Task(
			config=self.tasks_config['lead_profiling_task'],
			tools=[directory_read_tool,file_read_tool, search_tool]
		)

	@task
	def personalized_outreach_task(self) -> Task:
		return Task(
			config=self.tasks_config['personalized_outreach_task'],
			tools=[sentiment_analysis_tool, search_tool],
			output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the CustomerOutreach crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

import time
from litellm.exceptions import RateLimitError

def safe_llm_call(llm, **params):
    wait_time = 7  # starting wait time in seconds
    max_retries = 5
    for attempt in range(max_retries):
        try:
            return llm(**params)
        except RateLimitError as e:
            print(f"Rate limit reached. Waiting for {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            wait_time *= 2  # double the wait time for the next attempt
    raise Exception("Exceeded maximum retry attempts due to rate limits.")
