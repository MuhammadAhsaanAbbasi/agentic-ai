from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from automate_event_planning.tools.custom_tool import scrape_tool, search_tool
from pydantic import BaseModel
# Define a Pydantic model for venue details 
# (demonstrating Output as Pydantic)
class VenueDetails(BaseModel):
    name: str
    address: str
    capacity: int
    booking_status: str
# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AutomateEventPlanning():
	"""AutomateEventPlanning crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def venue_coordinator(self) -> Agent:
		return Agent(
			config=self.agents_config['venue_coordinator'],
			verbose=True,
			tools=[search_tool, scrape_tool]
		)

	@agent
	def logistics_manager(self) -> Agent:
		return Agent(
			config=self.agents_config['logistics_manager'],
			verbose=True,
			tools=[search_tool, scrape_tool]
		)
	
	@agent
	def marketing_communications_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['marketing_communications_agent'],
			verbose=True,
			tools=[search_tool, scrape_tool]
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def venue_task(self) -> Task:
		return Task(
			config=self.tasks_config['venue_task'],
			human_input=True,
			output_json=VenueDetails,
			output_file="venue_details.json"
		)

	@task
	def logistics_task(self) -> Task:
		return Task(
			config=self.tasks_config['logistics_task'],
			human_input=True,
			async_execution=False
		)
	
	@task
	def marketing_task(self) -> Task:
		return Task(
			config=self.tasks_config['marketing_task'],
			async_execution=True,
			output_file="marketing_report.md"
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the AutomateEventPlanning crew"""
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
