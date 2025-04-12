#!/usr/bin/env python
import sys
import warnings
import streamlit as st


from ai_news_letter.crew import AiNewsLetter

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

st.set_page_config(page_title="Panaversity", page_icon="📰", layout="wide")

st.title("Panaversity")
st.write("The Digital NewsLetter & Competitor of Perplexity 😱")


def run(topic: str):
    """
    Run the crew.
    """
    inputs = {
        'topic': topic,
    }
    
    try:
        result = AiNewsLetter().crew().kickoff(inputs=inputs)
        print(f"REsponse: {result}")
        response = result.model_dump()
        return {
            "response": response["raw"],
            "answer" : response
            }
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

news_topic = st.text_input("Enter a news topic")

if st.button("Generate News Letter"):
    if news_topic:
        result = run(news_topic)
        st.markdown(result["response"])
        st.write(result["answer"])
    else:
        st.error("Please enter a news topic.")
