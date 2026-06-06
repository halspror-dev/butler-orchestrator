from crewai import Agent, Task, Crew, LLM
import os

# CrewAI validates this at startup even for local models — set it to anything.
os.environ["OPENAI_API_KEY"] = "NA"

# Point CrewAI at your local Ollama. The "ollama/" prefix is REQUIRED.
llm = LLM(
    model="ollama/qwen3:14b",
    base_url="http://localhost:11434"
)

# Define one agent.
butler = Agent(
    role="Butler",
    goal="Answer the user's question clearly and concisely.",
    backstory="A calm, dry-witted AI assistant running locally on the user's hardware.",
    llm=llm,
    verbose=True
)

# Give it one task.
task = Task(
    description="Say hello and introduce yourself in two sentences.",
    expected_output="A two-sentence introduction.",
    agent=butler
)

# Wire them into a crew and run.
crew = Crew(agents=[butler], tasks=[task], verbose=True, tracing=False)
result = crew.kickoff()

print("\n\n=== RESULT ===")
print(result)