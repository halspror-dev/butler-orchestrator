import os
os.environ["OPENAI_API_KEY"] = "NA"

from crewai import Agent, Task, Crew, LLM, Process

# Worker models (fast, reliable) + a stronger manager model.
worker_llm = LLM(model="ollama/qwen3:14b", base_url="http://localhost:11434")
manager_llm = LLM(model="ollama/qwen3:14b", base_url="http://localhost:11434")

# Two specialist workers — note: NO fixed task order this time.
researcher = Agent(
    role="Researcher",
    goal="Find and list clear factual information on any topic given.",
    backstory="A focused analyst who gathers accurate facts.",
    llm=worker_llm,
    verbose=True
)

writer = Agent(
    role="Writer",
    goal="Turn information into clear, polished prose for a given audience.",
    backstory="A concise writer who shapes facts into clean summaries.",
    llm=worker_llm,
    verbose=True
)

# ONE high-level task. We do NOT assign it to a specific agent —
# the manager decides who handles it (and may use both).
mission = Task(
    description=(
        "Produce a beginner-friendly two-sentence explanation of how VLANs "
        "improve network security. Research the facts first, then write the summary."
    ),
    expected_output="A clear two-sentence beginner summary, grounded in real facts."
)

# Hierarchical crew: the manager LLM coordinates and delegates.
crew = Crew(
    agents=[researcher, writer],
    tasks=[mission],
    process=Process.hierarchical,
    manager_llm=manager_llm,
    verbose=True,
    tracing=False
)

result = crew.kickoff()

print("\n\n=== FINAL RESULT ===")
print(result)