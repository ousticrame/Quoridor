import asyncio
import os

from agents import Agent, Runner, function_tool
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled

from openai import AsyncOpenAI

from main import student_project_allocation

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://api.medium.text-generation-webui.myia.io/v1")
OPENAI_ENDPOINT_NAME = os.environ.get("OPENAI_ENDPOINT_NAME", "Qwen/QwQ-32B-AWQ")

client = AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
set_tracing_disabled(disabled=True)

from typing import List, Dict, Callable, Optional

@function_tool
def student_project_allocation_tool(
    students: List[int],
    projects: List[int],
    preferences: Dict[int, List[int]],
    project_capacities: Dict[int, int]) -> str:
    """
    Run the student project allocation algorithm.
    """
    print("Executing student project allocation tool")

    allocation =  student_project_allocation(students, projects, preferences, project_capacities, [])

    text = ''
    if allocation:
            for student, project in allocation.items():
                text += f"Student {student} is assigned to project {project}\n"

    return text

agent = Agent(
    name="Allocator boss",
    instructions="You are a helpful agent. You role is to allocate students to projects.",
    model=OpenAIChatCompletionsModel(model=OPENAI_ENDPOINT_NAME, openai_client=client),
    tools=[student_project_allocation_tool],
)

async def main():
    input_prompt = "I have a list of students and projects. Could you assist me in assigning students to projects, considering their preferences and project capacities? The students are [1, 2, 3], the projects are [101, 102], student preferences are {1: [101, 102], 2: [102, 101], 3: [101]}, and project capacities are {101: 2, 102: 1}."
    print("start")
    result = await Runner.run(agent, input=input_prompt)
    print("end")
    print(result.final_output)


def call_agent(input_prompt):
    result =asyncio.run(Runner.run(agent, input=input_prompt))
    print(result.final_output)
    return result.final_output

if __name__ == "__main__":
    asyncio.run(main())
