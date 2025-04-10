from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import PDFSearchTool

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

pdf_search_tool = PDFSearchTool(
	pdf="./knowledge/example_home_inspection.pdf",
	config=dict(
		llm=dict(
			provider="ollama", config=dict(model="deepseek-r1")
		),
		embedder=dict(
			provider="ollama", config=dict(model="all-minilm")
		)
	)
)

@CrewBase
class PdfRag():
	"""PdfRag crew"""

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def researcher(self) -> Agent:
		return Agent(
			role='Researcher Agent',
			goal='Research the topic through pdf to find relevant answers',
			backstory=(
				"""
			The research agent is adept at searching and extracting data 
			from documents, ensuring accurate and prompt responses.
		"""
			),
			tools=[pdf_search_tool],
			allow_delegation=False,
			verbose=True
		)

	@agent
	def professional_writter(self) -> Agent:
		return Agent(
			role='Professional Writter Agent',
			goal="Write a professional emails based on the research agent's findings",
			backstory=(
				"""
			The professional writter agent has excellent writing skills and is able 
			to craft clear & concise emails based on the provided information.
		"""
			),
			allow_delegation=False,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def answer_customer_question(self) -> Task:
		return Task(
			description=(
				"""
			Answer the customer's question based on the home inspection PDF.
			The research agent will search through the PDF to find relevant information.
			Your final answer MUST be clear and accurate, based on the content of the
			home inspection PDF.
			
			Here is the customer's question:
			{customer_question}
		"""
			),
		expected_output="""
			Provide clear and accurate answers to the customer's question.
			Your answer MUST be based on the content of the home inspection PDF.
		""",
		agent=self.researcher(),
		tools=[pdf_search_tool]
)

	@task
	def write_email_task(self) -> Task:
		return Task(
			description=(
				"""
			- Write a professional email to a contractor based
				on the research agent's findings.
			- The email should clearly state the issues found in the specified section
				of the report and request a quote or action plan for fixing these issues.

				Best Regards,

				M.Ahsaan Abbasi,
				Abbasi Realty
			"""
			),
			expected_output="""
			Write a clear and concise email that can be sent to a contractor to address the issues found in the home inspection report
		""",
		agent=self.professional_writter(),
		output_file='report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the PdfRag crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)


crew = PdfRag().crew()

customer_question = input(
    "Which section of the report would you like to generate a work order for?\n"
)

result = crew.kickoff(inputs={"customer_question": customer_question})

print(f"REsponse: {result}")