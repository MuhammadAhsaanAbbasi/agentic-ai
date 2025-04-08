from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
from nodes.nodes import Nodes
from nodes.state import EmailsState
from email_assistant_crew.crew import EmailFilterAgent

_ = load_dotenv()


class EmailWorkflow():
    def __init__(self):
        nodes = Nodes()
        workflow = StateGraph(EmailsState)

        agent = EmailFilterAgent()

        workflow.add_node("check_new_emails", nodes.check_new_emails)
        workflow.add_node("wait_next_run", nodes.wait_next_run)
        workflow.add_node("draft_responses", agent.kickoff)

        workflow.set_entry_point(START, "check_new_emails")

        workflow.add_conditional_edges(
            "check_new_emails",
            nodes.new_email,
            {
                "continue": "draft_responses",
                "end": "wait_next_run"
            }
        )

        workflow.add_edge("draft_responses", "wait_next_run")
        workflow.add_edge("wait_next_run", "check_new_emails")

        self.app = workflow.compile()