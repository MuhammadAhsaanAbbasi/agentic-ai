#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from job_application_crew.crew import JobApplicationCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    job_application_inputs = {
    'job_posting_url': 'https://jobs.lever.co/AIFund/6c82e23e-d954-4dd8-a734-c0c2c5ee00f1?lever-origin=applied&lever-source%5B%5D=AI+Fund',
    'github_url': 'http://github.com/muhammadAhsaanAbbasi',
    'personal_writeup': """M.Ahsaan Abbasi is a Full Stack Developer with hands-on experience in 
    React, Next.js, & JAMStack frameworks. I’m also proficient in Python, FastAPI, and the MERN Stack, 
    as well as creating AI-driven solutions with LangChain and Large Language Models. I specialize in 
    UI design with Tailwind CSS and have extensive experience setting up efficient CI/CD pipelines. 
    My goal is always to integrate cutting-edge AI solutions that enhance user engagement and 
    drive revenue."""
    }
    
    try:
        JobApplicationCrew().crew().kickoff(inputs=job_application_inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        JobApplicationCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        JobApplicationCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        JobApplicationCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
