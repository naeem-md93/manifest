from copy import deepcopy

from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

from manifest.utils import llm_utils
from manifest.schemas import ManifestState


SYSTEM_PROMPT = """
تو یک مدیر پروژه در یک سیستم پیاده سازی پروژه هستی.
وظیفه تو اینه که اسناد برنامه پیاده سازی به همراه گزارشات پیاده سازی قابلیت های قدیمی رو مطالعه کنی و تصمیم بگیری که آیا پروژه به طور کامل و دقیق پیاده سازی شده یا نه.
اگر کامل پیاده سازی شده بود باید به صورت دقیق اینو اعلام کنی و is_finished=True. در غیر این صورت باید بررسی کنی و ببینی کدوم قسمت پروژه هنوز پیاده سازی نشده و قابلیت بعدی که باید پیاده سازی بشه رو مشخص کنی.

فرمت خروجیت باید به صورت زیر باشه:

# فرمت خروجی:
{format_instructions}
"""


class Schema(BaseModel):
    reasoning: str = Field(..., description="Your internal reasoning and chain of thoughts about your decision.")
    is_finished: bool = Field(..., description="Whether the project is completely implemented or not.")
    selected_feature: str = Field(..., description="The next selected feature to implement.")


class ProjectManagerAgent:
    def __init__(self):
        self.llm = llm_utils.build_language_model(
            name="project_manager_model",
            temperature=0.3,
            max_tokens=1500
        )
        self.parser = PydanticOutputParser(pydantic_object=Schema)

        self.chain = self.llm | self.parser

    def invoke(self, state: ManifestState) -> None:

        messages = [
            {"role": "system", "content": deepcopy(SYSTEM_PROMPT).format(
                format_instructions=self.parser.get_format_instructions()
            )},
            {"role": "system", "content": state.documents[""]}
        ]