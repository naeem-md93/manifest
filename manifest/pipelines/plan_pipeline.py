from typing import Any

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
You are a planning agent in a Multi-Agent Web-App Development System.

# Task:
Given a project request document, your job is to analyze it and gather enough information for breaking down the project into implementation phases.
You must use the `write_document_tool` to write and store the implementation roadmap document.
Each step in your implementation roadmap document must be a user-facing, valuable feature that can be delivered to end users and stakeholders.
The first step in your implementation document must be a "Hello World Generator" which is for preparing the environment and setting up the project directory.
Implementation steps must be in the order of implementation.

# Available Tools:
- **`web_search_tool(query: str)`:** You can use this tool to search one the Internet.
- **`write_document_tool(agent_name='plan', document: str)`:** You can use this tool to write and store an implementation roadmap document.

# Rules:
- Your responses must be short.
- The implementation roadmap document must be less than 1000 words.
- You MUST ALWAYS use the `write_document_tool` tool to write and store the project request document.
"""


class PlanPipeline:
    def __init__(self):
        self.llm = llm_utils.build_language_model(
            f"{Agents.PLAN}_model",
            temperature=0.3,
            max_tokens=2000
        )
        self.agent = create_agent(
            name=f"{Agents.PLAN}_agent",
            model=self.llm,
            tools=[write_document_tool, web_search_tool]
        )

    def invoke(self, user_message: str, state: ManifestState) -> str:

        if not state.documents[Agents.BRAINSTORM]:
            return "Brainstorm document not found."

        if not state.messages.get(Agents.PLAN):
            state.messages[Agents.PLAN] = []

        messages: list[AnyMessage] = [
            SystemMessage(name=Agents.PLAN, content=SYSTEM_PROMPT),
            SystemMessage(name=Agents.BRAINSTORM, content="## Project Request Document:\n\n" + state.documents[Agents.BRAINSTORM][-1])
        ] + state.messages[Agents.PLAN] + [
            HumanMessage(user_message)
        ]

        py_utils.write_text_file(state.history_path, log_utils.reformat_messages(messages))

        ai_response: str = ""
        for event in self.agent.stream({"messages": messages}, context=state):
            if "model" in event:
                st: dict[str, Any] = event["model"]
            elif "tool" in event:
                st: dict[str, Any] = event["tool"]

            py_utils.append_text_file(state.history_path, log_utils.reformat_message(st["messages"][-1]))
            ai_response = st["messages"][-1].content

        state.messages[Agents.PLAN].append(HumanMessage(user_message))
        state.messages[Agents.PLAN].append(AIMessage(name=Agents.PLAN, content=ai_response))

        return ai_response