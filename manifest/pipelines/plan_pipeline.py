from typing import Generator
from langchain.agents import create_agent

from manifest.utils import llm_utils
from manifest.schemas import ManifestState
from manifest.tools.write_document_tool import write_document_tool


SYSTEM_PROMPT = """
تو یک ربات دستیار هستی که در یک سیستم پیاده سازی پروژه نقش فاز بندی پروژه را برعهده داری.
زمانی که یک درخواست پروژه به دستت رسید. باید اون رو به قاز های مختلف برای پیاده سازی تقسیم کنی.
ترتیب فاز ها باید به ترتیب پیاده سازی باشن.

برای تقسیم کردن پروژه باید از ابزار write_document_tool استفاده کنی. پارامتر agent_name همیشه باید برابر با Plan باشد.
"""


class PlanPipeline:
    def __init__(self):
        self.llm = llm_utils.build_language_model(
            "Plan_model",
            temperature=0.0,
            max_tokens=2000
        )
        self.agent = create_agent(
            name="Plan_agent",
            model=self.llm,
            tools=[write_document_tool]
        )

    def invoke(self, user_message: str, state: ManifestState) -> str:

        if not state.documents["Brainstorm"]:
            return "Brainstorm document not found."

        st: dict[str, list[dict[str, str]]] = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": state.documents["Brainstorm"]},
            ]
        }
        st["messages"] += state.conversations["Plan"]
        st["messages"].append({"role": "user", "content": user_message})

        ai_response: str = ""
        for event in self.agent.stream(st, context=state):
            if "model" in event:
                s = event["model"]
            elif "tool" in event:
                s = event["tool"]
            ai_response = s["messages"][-1].content

        return ai_response