import openai

openai.api_key="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",



try:
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt="Hello, world!",
        max_tokens=5
    )
    print(response.choices[0].text.strip())
except Exception as e:
    print(f"An error occurred: {e}")