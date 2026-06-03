import os
os.environ["OPENAI_API_KEY"] = "NA"

from crewai import Agent, Task, Crew, LLM, Process

worker_llm = LLM(model="ollama/qwen3:8b", base_url="http://localhost:11434")
manager_llm = LLM(model="ollama/qwen3:14b", base_url="http://localhost:11434")

# THREE specialists now.
researcher = Agent(
    role="Researcher",
    goal="Gather accurate, specific factual information on the assigned topic. You ONLY research; you do not write final prose.",
    backstory="A focused analyst who gathers raw facts and hands them off.",
    llm=worker_llm,
    verbose=True
)

writer = Agent(
    role="Writer",
    goal="Turn researched facts into clear, polished prose for the target audience. You ONLY write; you rely on the Researcher's facts.",
    backstory="A concise writer who shapes facts into clean summaries.",
    llm=worker_llm,
    verbose=True
)

fact_checker = Agent(
    role="Fact Checker",
    goal="Review a written summary against the original facts and flag any inaccuracies or unsupported claims. You ONLY verify; you do not rewrite.",
    backstory="A meticulous reviewer who confirms accuracy before anything is finalized.",
    llm=worker_llm,
    verbose=True
)

# One mission that REQUIRES all three roles, so the manager must delegate to each.
mission = Task(
    description=(
        "Produce a verified, beginner-friendly two-sentence explanation of how VLANs "
        "improve network security. You must: (1) have the Researcher gather the facts, "
        "(2) have the Writer turn those facts into the two-sentence summary, and "
        "(3) have the Fact Checker verify the summary is accurate against the research "
        "before finalizing. Delegate each step to the appropriate specialist."
    ),
    expected_output="A fact-checked, beginner-friendly two-sentence summary about VLAN security."
)

crew = Crew(
    agents=[researcher, writer, fact_checker],
    tasks=[mission],
    process=Process.hierarchical,
    manager_llm=manager_llm,
    verbose=True,
    tracing=False
)

result = crew.kickoff()

print("\n\n=== FINAL RESULT ===")
print(result)