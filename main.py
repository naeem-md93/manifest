from manifest.workflow import build_graph


project_dir: str = "./task_01"
project_description: str = """
We want to build a simple web application where users can sign up, log in, and manage a list of personal notes.
Users should be able to:
Register with email and password
Log in and log out
Create, view, update, and delete their own notes
The frontend should be a single-page application using React.
The backend should expose a REST API using Python & FastAPI.
Data should be persisted in a SQLite database.
Authentication must be secure, and users must not access other users’ notes.
The system should be easy to extend later.
"""


GRAPH = build_graph()


if __name__ == "__main__":
    GRAPH.invoke({
        "project_dir": project_dir,
        "project_description": project_description,
    })