from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_community.agent_toolkits import GmailToolkit
from langchain_community.tools.gmail import GmailGetThread
from langchain_community.tools import TavilySearchResults
from .tools.custom_tool import GmailDraftor
from langchain_community.tools.gmail import get_gmail_credentials
import os

current_file_path = os.path.abspath(__file__)
# print(f"current file: {current_file_path}")

# Get the parent directory of the current file's directory
parent_directory = os.path.dirname(current_file_path)
# print(f"parent file: {parent_directory}")

# Get the parent directory of the parent directory
Child_DIR = os.path.dirname(parent_directory)


# Get the Chlid directory of the parent directory
BASE_DIR = os.path.dirname(Child_DIR)

# print(f"BASE_DIR: {BASE_DIR}")

# Define the path to the client_secret.json file
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'credentials.json')

# print(f'secret file: {CLIENT_SECRET_FILE}')
resource = get_gmail_credentials(client_secrets_file=CLIENT_SECRET_FILE)

@CrewBase
class EmailFilterAgent():
	"""EmailAssistant crew"""

	def __init__(self, state):
		self.gmail = GmailToolkit(api_resource=resource).model_rebuild()
		self.state = state

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def email_filter_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['email_filter_agent'],
		)

	@agent
	def email_action_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['email_action_agent'],
			tools=[
				GmailGetThread(api_resource=self.gmail.api_resource),
				TavilySearchResults()
			]
		)
	
	@agent
	def email_response_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['email_response_writer'],
			tools=[
				TavilySearchResults(),
				GmailGetThread(api_resource=self.gmail.api_resource),
				GmailDraftor()
			]
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def filter_emails(self) -> Task:
		return Task(
			config=self.tasks_config['filter_emails'],	
		)

	@task
	def action_required_emails(self) -> Task:
		return Task(
			config=self.tasks_config['action_required_emails'],
		)

	@task
	def draft_responses(self) -> Task:
		return Task(
			config=self.tasks_config['draft_responses'],
			output_file='REPORT.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the 01EmailAssistant crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
	
	def kickoff(self, state):
		"""Starts the """
		crew = self.crew()
		result = crew.kickoff(inputs={'emails': state["emails"]})
		print(result)

		return {**state, "action_required_emails": result}
