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

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("allocation_ai.log"), logging.StreamHandler()],
)
logger = logging.getLogger("allocation_ai")


@dataclass
class PotentialData:
    image: BytesIO | None
    benchmark_info: Dict[str, Any] | None = None


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
    logger.info("Executing student project allocation tool")
    logger.info(f"Input: {len(students)} students, {len(projects)} projects")

    # Call the student_project_allocation function, which now returns benchmark info
    allocation, benchmark_info = student_project_allocation(
        students, projects, preferences, project_capacities, []
    )

    # Store benchmark info in the context for later use
    wrapper.context.benchmark_info = benchmark_info
    logger.info(f"Benchmark info: {benchmark_info}")

    # Build the response text
    text = ""

    # First add benchmarking information
    text += "## Algorithm Benchmarking\n\n"
    text += "| Algorithm | Score | Time (s) | Solution Found |\n"
    text += "|-----------|-------|----------|---------------|\n"

    for algo_name, results in benchmark_info.items():
        if algo_name not in ["best_algorithm", "best_score"]:
            score = results.get("score")
            time = results.get("time")
            solution = "Yes" if results.get("solution_found", False) else "No"

            score_display = f"{score:.4f}" if score is not None else "N/A"
            time_display = f"{time:.4f}" if time is not None else "N/A"

            text += f"| {algo_name} | {score_display} | {time_display} | {solution} |\n"

    best_algo = benchmark_info.get("best_algorithm")
    best_score = benchmark_info.get("best_score")

    if best_algo and best_score is not None:
        text += f"\nBest algorithm: **{best_algo}** with score {best_score:.4f}\n\n"
    else:
        text += "\nNo algorithm was able to find a valid solution.\n\n"

    if allocation:
        # Then add allocation details
        text += "## Allocation Results\n\n"
        text += "| Student | Project | Preference Rank |\n"
        text += "|---------|---------|----------------|\n"

        # Calculate preference satisfaction
        satisfied = 0
        total = len(students)

        for student in sorted(allocation.keys()):
            project = allocation[student]
            if student in preferences and project in preferences[student]:
                pref_idx = preferences[student].index(project) + 1  # 1-based rank
                rank_text = f"#{pref_idx}"
                satisfied += 1
            else:
                rank_text = "Not in preferences"

            text += f"| {student} | {project} | {rank_text} |\n"

        # Add summary of preference satisfaction
        if total > 0:
            satisfaction_rate = (satisfied / total) * 100
            text += f"\n### Preference Satisfaction Summary\n\n"
            text += f"- **Satisfaction Rate**: {satisfaction_rate:.1f}%\n"
            text += (
                f"- **Students with Preferred Projects**: {satisfied} out of {total}\n"
            )

            # Add preference distribution
            if satisfied > 0:
                text += "\n**Preference Distribution:**\n\n"
                rank_counts = {}
                for student, project in allocation.items():
                    if student in preferences and project in preferences[student]:
                        rank = preferences[student].index(project) + 1
                        rank_counts[rank] = rank_counts.get(rank, 0) + 1

                for rank in sorted(rank_counts.keys()):
                    count = rank_counts[rank]
                    percentage = (count / total) * 100
                    text += (
                        f"- Preference #{rank}: {count} students ({percentage:.1f}%)\n"
                    )
    else:
        text += "No valid allocation could be found with the given constraints."

    # Generate visualization
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

        # Include best algorithm info in the title if available
        if best_algo and best_score is not None:
            plt.title(
                f"Student Project Allocation (Best: {best_algo}, Score: {best_score:.4f})"
            )
        else:
            plt.title("Student Project Allocation")

        plt.tight_layout()  # Adjust layout to prevent labels from overlapping

        # Convert the plot to an image in memory
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        plt.close()

        # Store the image in the context
        wrapper.context.image = buf
        logger.info("Successfully generated and stored the allocation image.")
    else:
        wrapper.context.image = None
        plt.close()
        logger.warning("No allocation found, so no image was generated.")

    return text


agent = Agent(
    name="Allocator boss",
    instructions="""
    You are an expert assistant specializing in student-project allocation problems using constraint satisfaction.
    
    Your primary capabilities:
    1. You help allocate students to projects based on their preferences, project capacities, and additional constraints.
    2. You benchmark multiple allocation algorithms (CP-SAT, Greedy, Random) and select the best solution.
    3. You can explain the allocation results clearly, including visualization through tables.
    4. You provide insights on how well the allocation satisfies student preferences.
    
    When users interact with you:
    - Extract clear information about students, projects, preferences, and capacities from their descriptions.
    - Present benchmarking results for different allocation algorithms.
    - Explain which algorithm performed best and why.
    - Provide detailed allocation results with preference satisfaction metrics.
    - Provide the benchmarking information in a structured format, like a table.
    - Use concrete examples when explaining concepts.
    
    If no valid allocation can be found:
    - Explain why the constraints might be too restrictive.
    - Suggest possible modifications to make the problem solvable.
    
    Be precise and helpful, focus on delivering clear explanations of allocation problems and their solutions.
    """,
    model=OpenAIChatCompletionsModel(model=OPENAI_ENDPOINT_NAME, openai_client=client),
    tools=[student_project_allocation_tool],
)


def call_agent(input_prompt) -> Dict[str, Any]:
    logger.info(f"Calling agent with input: {input_prompt}")
    context = PotentialData(image=None, benchmark_info=None)
    result = asyncio.run(Runner.run(agent, input=input_prompt, context=context))

    result_obj = {
        "final_output": result.final_output,
        "image": context.image,
        "benchmark_info": context.benchmark_info,  # Pass benchmarking info to UI if needed
    }
    logger.info(
        f"Agent call completed, benchmark info: {context.benchmark_info is not None}"
    )

    logger.info(f"Final output: {result.final_output}")

    return result_obj
