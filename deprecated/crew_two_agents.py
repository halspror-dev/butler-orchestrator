import os

# Kill all CrewAI cloud telemetry/tracing — keep everything local
os.environ["CREWAI_TRACING_ENABLED"] = "false"
os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
os.environ["OTEL_SDK_DISABLED"] = "true"
os.environ["OPENAI_API_KEY"] = "NA"

from crewai import Agent, Task, Crew, LLM
from crewai import Agent, Task, Crew, LLM
import os

os.environ["OPENAI_API_KEY"] = "NA"

# Two workers, both on a clean tool-capable model for now.
llm = LLM(
    model="ollama/qwen3:14b",
    base_url="http://localhost:11434"
)

# Agent 1: the researcher/thinker.
researcher = Agent(
    role="Researcher",
    goal="Produce clear, factual notes on the topic you're given.",
    backstory="A focused analyst who gathers and organizes information.",
    llm=llm,
    verbose=True
)

# Agent 2: the writer, who works from the researcher's output.
writer = Agent(
    role="Writer",
    goal="Turn research notes into a short, polished summary.",
    backstory="A concise writer who shapes raw notes into clean prose.",
    llm=llm,
    verbose=True
)

# Task 1: researcher does this first.
research_task = Task(
    description="List three key facts about how VLANs improve network security.",
    expected_output="Three concise factual bullet points.",
    agent=researcher
)

# Task 2: writer does this, using the researcher's output as context.
write_task = Task(
    description="Using the research notes, write a two-sentence summary a beginner could understand.",
    expected_output="A clear two-sentence summary.",
    agent=writer,
    context=[research_task]   # <-- THIS is the hand-off: task 2 receives task 1's output
)

crew = Crew(
    agents=[researcher, writer],
    tasks=[research_task, write_task],
    verbose=True,
    tracing=False
)

result = crew.kickoff()

print("\n\n=== FINAL RESULT ===")
print(result)