from services.agent import run_news_workflow
import chainlit as cl

@cl.on_message
async def main(message: cl.Message):
    """
    Main function to handle the message from the user and generate a response.
    """
    
    topic = message.content

    await cl.Message(
        content=f"Searching for news on {topic}...",
        author="News Bot"
    ).send()

    try:
        response = run_news_workflow(topic)
        await cl.Message(
            content=response,
            author="News Bot"
        ).send()
    except Exception as e:
        await cl.Message(
            content=f"Error: {e}",
            author="News Bot"
        ).send()


@cl.on_chat_start
async def start():
    """
    Function to handle the start of the chat.
    """
    await cl.Message(
        content="Welcome to the News Assistant! What topic would you like to get news about.",
        author="News Bot"
    ).send()