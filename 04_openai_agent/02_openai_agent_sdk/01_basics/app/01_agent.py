from agents import Agent, Runner

math_agent = Agent(
    name="Math Professor",
    instructions="You're helpful Math professor that's help students to resolve their quries."
)

result = Runner.run_sync(math_agent, "What is Distributive Law & solve it with a set of A & B, first five primary number is in set A, first five even number in set B")

print(result.final_output)