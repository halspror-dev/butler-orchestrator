import os
os.environ["OPENAI_API_KEY"] = "NA"

from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import CodeInterpreterTool

# Code runs in an isolated Docker container. unsafe_mode is explicitly OFF —
# this is the line between "sandboxed" and "RCE on your host."
code_tool = CodeInterpreterTool(unsafe_mode=False)

worker_llm = LLM(model="ollama/qwen3:14b", base_url="http://localhost:11434")

# A worker that can actually RUN code, not just write it.
coder = Agent(
    role="Code Executor",
    goal="Solve computational problems by writing and ACTUALLY RUNNING Python code, then reporting the real output.",
    backstory="A precise programmer who never guesses a result — always executes the code and reads the actual output.",
    llm=worker_llm,
    tools=[code_tool],
    verbose=True
)

task = Task(
    description="Calculate the SHA-256 hash of the string 'butler test' by writing and running Python code. Report the actual hash the code produces.",
    expected_output="The real 64-character SHA-256 hash, produced by executing code.",
    agent=coder
)

crew = Crew(
    agents=[coder],
    tasks=[task],
    process=Process.sequential,
    verbose=True,
    tracing=False
)

result = crew.kickoff()

print("\n\n=== FINAL RESULT ===")
print(result)