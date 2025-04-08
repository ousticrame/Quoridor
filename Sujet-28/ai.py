import asyncio
from io import BytesIO
import os

from PIL.ImageFile import Image
from agents import Agent, Runner, function_tool, ToolCallOutputItem, RunContextWrapper
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    function_tool,
    set_tracing_disabled,
)

from openai import AsyncOpenAI

from main import student_project_allocation


OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_BASE_URL = os.environ.get(
    "OPENAI_BASE_URL", "https://api.medium.text-generation-webui.myia.io/v1"
)
OPENAI_ENDPOINT_NAME = os.environ.get("OPENAI_ENDPOINT_NAME", "Qwen/QwQ-32B-AWQ")

client = AsyncOpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
set_tracing_disabled(disabled=True)

from typing import List, Dict, Callable, Optional, Any

from dataclasses import dataclass


@dataclass
class PotentialData:
    image: BytesIO | None


@function_tool
def student_project_allocation_tool(
    wrapper: RunContextWrapper[PotentialData],
    students: List[int],
    projects: List[int],
    preferences: Dict[int, List[int]],
    project_capacities: Dict[int, int],
) -> str:
    """
    Run the student project allocation algorithm and generate an image of the allocation.
    """
    print("Executing student project allocation tool")

    allocation: Optional[Dict[int, int]] = student_project_allocation(
        students, projects, preferences, project_capacities, []
    )

    text = ""
    if allocation:
        for student, project in allocation.items():
            text += f"Student {student} is assigned to project {project}\n"
    else:
        text = "No valid allocation could be found with the given constraints."

    import matplotlib.pyplot as plt
    import networkx as nx
    import io

    # Create a graph representation of the allocation
    G = nx.Graph()
    if allocation:
        plt.clf()
        for student, project in allocation.items():
            G.add_node(f"Student {student}", type="student")
            G.add_node(f"Project {project}", type="project")
            G.add_edge(f"Student {student}", f"Project {project}")

        # Visualize the graph
        pos = nx.spring_layout(
            G, k=0.5, iterations=50
        )  # Adjust k and iterations for better spacing
        student_nodes = [
            node for node, data in G.nodes(data=True) if data.get("type") == "student"
        ]
        project_nodes = [
            node for node, data in G.nodes(data=True) if data.get("type") == "project"
        ]

        plt.figure(figsize=(10, 8))  # Increase figure size for better readability
        nx.draw_networkx_nodes(
            G, pos, nodelist=student_nodes, node_color="skyblue", node_size=800
        )
        nx.draw_networkx_nodes(
            G, pos, nodelist=project_nodes, node_color="lightgreen", node_size=1200
        )
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5)
        nx.draw_networkx_labels(G, pos, font_size=12, font_family="sans-serif")
        plt.title("Student Project Allocation")
        plt.tight_layout()  # Adjust layout to prevent labels from overlapping

        # Convert the plot to an image in memory
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        # Store the image in the context
        wrapper.context.image = buf
    else:
        wrapper.context.image = None
        plt.close()

    return text


agent = Agent(
    name="Allocator boss",
    instructions="You are a helpful agent. You help in all matters of life. One of your tasks is to allocate students to projects.",
    model=OpenAIChatCompletionsModel(model=OPENAI_ENDPOINT_NAME, openai_client=client),
    tools=[student_project_allocation_tool],
)

# async def main():
#     input_prompt = "I have a list of students and projects. Could you assist me in assigning students to projects, considering their preferences and project capacities? The students are [1, 2, 3], the projects are [101, 102], student preferences are {1: [101, 102], 2: [102, 101], 3: [101]}, and project capacities are {101: 2, 102: 1}."
#     print("start")
#     result = await Runner.run(agent, input=input_prompt)
#     print(result.new_items)

#     image_item = next((item for item in result.new_items if isinstance(item, ToolCallOutputItem)), None)
#     if image_item and image_item.output and 'image' in image_item.output:
#         image = image_item.output['image']
#         # Process the image as needed (e.g., save to file)
#         # For demonstration, let's just print some info
#         print(f"Image data: {type(image)}, length: {len(image)}")

#     print("end")
#     print(result.final_output)


def call_agent(input_prompt) -> Dict[str, Any]:
    context = PotentialData(image=None)
    result = asyncio.run(Runner.run(agent, input=input_prompt, context=context))
    # print(result)

    # image = None
    # image_item = next((item for item in result.new_items if isinstance(item, ToolCallOutputItem)), None)
    # if image_item and image_item.output and 'image' in image_item.output:
    #     image = image_item.output['image']
    #     # Process the image as needed (e.g., save to file)
    #     # For demonstration, let's just print some info
    #     print(f"Image data: {type(image)}, length: {len(image)}")

    # # print(result.final_output)
    # #
    result_obj = {
        "final_output": result.final_output,
        "image": context.image,
    }
    print(result_obj)

    return result_obj

    # if __name__ == "__main__":
    #     asyncio.run(main())
