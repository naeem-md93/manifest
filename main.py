import os

from manifest.subgraphs.understanding.workflow import build_graph


project_dir: str = "./life_manager"
project_description: str = """
I want to build a web-based life and goal management application that uses AI agents and LLMs to help users\
 clarify their goals, turn them into actionable plans, and keep those plans up to date over time.
The system will guide users through goal definition, generate a planning schedule,\
 and run regular check-ins (for example, nightly) to collect feedback and automatically adjust the\
 schedule when needed. All planned tasks and events will be synced to an external calendar,\
 such as Google Calendar or a CalDAV-based calendar compatible with GNOME Calendar.
The application will include simple email-and-password authentication,\
 a React + JavaScript frontend, and a Python backend built with FastAPI.\
 Data will be stored in SQLite for the initial version.
"""


UNDERSTANDING_GRAPH = build_graph()


if __name__ == "__main__":
    os.makedirs(project_dir, exist_ok=True)
    os.makedirs(f"{project_dir}/.manifest_cache/", exist_ok=True)
    UNDERSTANDING_GRAPH.invoke({
        "project_dir": project_dir,
        "project_desc": project_description,
        "checkpoints_path": f"{project_dir}/.manifest_cache/"
    })