from langchain.agents import create_agent
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    AIMessage,
    AnyMessage
)

from manifest.entities import Agents
from manifest.schemas import ManifestState
from manifest.utils import llm_utils, py_utils, log_utils
from manifest.tools.web_search_tool import web_search_tool
from manifest.tools.write_document_tool import write_document_tool


SYSTEM_PROMPT = """\
# Role:
You are a helpful brainstorming assistant in a Multi-Agent Web-App Development Environment.

# Task:
Given a project description, your job is to explore the project request and exchange ideas and help user with brainstorming.
- You can talk or ask about ambiguities, improve mentioned features, suggest new features, warn about bugs or inconsistencies.
- You can help user explore all possible user-stories, happy paths, edge cases, etc.
- Generally, your job is to understand what the user wants and convert its intention into a project request document.

# Available Tools:
- **`web_search_tool(query: str)`:** You can use this tool to search one the Internet.
- **`write_document_tool(agent_name='brainstorm', document: str)`:** You can use this tool to write and store a project request document.

# Rules:
- Your response must be less than 300 words.
- The project request document must be less than 500 words.
- You MUST ALWAYS use the `write_document_tool` tool to write and store the project request document.
"""


class BrainstormPipeline:
    def __init__(self):
        self.llm = llm_utils.build_language_model(
            f"{Agents.BRAINSTORM}_model",
            temperature=0.7,
            max_tokens=2000
        )
        self.agent = create_agent(
            name=f"{Agents.BRAINSTORM}_agent",
            model=self.llm,
            tools=[web_search_tool, write_document_tool]
        )

    def invoke(self, user_message: str, state: ManifestState) -> str:

        if not state.messages.get(Agents.PLAN):
            state.messages[Agents.BRAINSTORM] = []

        messages: list[AnyMessage] = [
           SystemMessage(name=Agents.BRAINSTORM, content=SYSTEM_PROMPT),
        ] + state.messages[Agents.BRAINSTORM] + [
            HumanMessage(user_message),
        ]

        py_utils.write_text_file(state.history_path, log_utils.reformat_messages(messages))

        ai_response: str = ""
        for event in self.agent.stream({"messages": messages}, context=state):
            if "model" in event:
                st = event["model"]
            elif "tools" in event:
                st = event["tools"]

            py_utils.append_text_file(state.history_path, log_utils.reformat_message(st["messages"][-1]))
            ai_response = st["messages"][-1].content

        state.messages[Agents.BRAINSTORM].append(HumanMessage(user_message))
        state.messages[Agents.BRAINSTORM].append(AIMessage(name=Agents.BRAINSTORM, content=ai_response))

        return ai_response