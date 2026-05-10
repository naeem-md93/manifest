from typing import Any
from typing import Callable

import os
import time
import requests
from openai import OpenAI
from langchain_core.documents import Document
from pydantic import BaseModel, SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.messages import AnyMessage, AIMessage, ToolMessage, HumanMessage
from langchain_core.runnables import RunnableSerializable


class EmbeddingModel:
    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model_name: str | None = None
    ):
        self.model = OpenAI(
            base_url=base_url or os.getenv("EMBEDDING_BASE_URL"),
            api_key=api_key or os.getenv("EMBEDDING_API_KEY"),
        )
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL")

    def embed_documents(self, texts: list[str] | list[str]) -> list[list[float]]:
        resp = self.model.embeddings.create(
            input=texts,
            model=self.model_name
        )
        resp = [d.embedding for d in resp.data]
        return resp

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


def build_embedding_model(
    name: str = "unknown_embedding_model",
    base_url: str | None = None,
    api_key: str | None = None,
    model_name: str | None = None,
):
    model = EmbeddingModel(
        model_name=model_name,
        base_url=base_url,
        api_key=api_key
    )

    return model


def build_language_model(
        name: str = "unknown",
        base_url: str | None = None,
        api_key: str | SecretStr | None = None,
        model_name: str | None = None,
        temperature: int | float = 0,
        max_tokens: int | None = None
):
    model = ChatOpenAI(
        name=name,
        base_url=base_url or os.getenv("LANGUAGE_BASE_URL"),
        api_key=api_key or os.getenv("LANGUAGE_API_KEY"),
        model=model_name or os.getenv("LANGUAGE_MODEL"),
        max_tokens=max_tokens,
        temperature=temperature
    )

    return model


def run_chain_with_retry(
        chain: RunnableSerializable,
        inputs: dict[str, Any],
        max_retry: int = 5,
        retry_interval: int = 3,
        validator_fn: Callable | None = None,
        validator_inputs: dict[str, Any] | None = None,
) -> BaseModel | str:
    resp_obj = None
    prev_attempts = ""
    kwargs: dict[str, Any] = {"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}
    if validator_inputs is None:
        validator_inputs = {}

    for i in range(max_retry):
        try:
            resp_obj = chain.invoke({
                "prev_attempts": prev_attempts or "None",
                **inputs,
                **kwargs
            })

            if validator_fn is not None:
                validator_fn(resp_obj, **validator_inputs)

            break
        except Exception as e:
            err_msg = f"Attempt {i + 1} failed due to: {repr(e)}"

            prev_attempts += "==========\n"
            prev_attempts += f"Attempt {i + 1} Failed.\n"
            prev_attempts += "----------\n"
            prev_attempts += f"Your Response:\n{resp_obj}\n"
            prev_attempts += "----------\n"
            prev_attempts += f"Error:\n{err_msg}\n"
            prev_attempts += "==========\n\n"

            print(err_msg)
            print(f"Waiting {retry_interval} seconds...")
            time.sleep(retry_interval)

    if resp_obj is None:
        raise RuntimeError(f"Failed after {max_retry} attempts: {prev_attempts}")

    return resp_obj


def remove_fences(content: str) -> str:
    if content.startswith("```"):
        first_word = content.split("\n")[0]
        content = content[len(first_word):]

    if content.endswith("```"):
        content = content[:-3]

    return content


def reformat_stream_event(event: dict[str, Any]) -> str:
    result: str = ""

    for name, values in event.items():
        for msg in values["messages"]:

            if isinstance(msg, AIMessage):
                sender: str = "Agent"
            elif isinstance(msg, ToolMessage):
                sender: str = "Tool"
            else:
                sender: str = "Unknown"

            name: str = getattr(msg, "name", "")
            content: str = getattr(msg, "content", "")
            tool_calls: list[dict[str, Any]] = getattr(msg, "tool_calls", [])

            result += f"## `{name}` {sender} Message:\n\n"
            result += f"#### {content}\n\n"

            if tool_calls:
                result += f"#### Tool Calls:\n\n"
                for tc in tool_calls:
                    result += f"* #### \t Name: `{tc['name']}`\n\n"
                    result += f"* #### \t Args:\n\n"
                    for arg_name, arg_value in tc['args'].items():
                        result += f"\t\t{arg_name}:\n"
                        result += str(arg_value) + "\n\n"

            result += "# ********************************\n\n"

    return result


def get_final_document(messages: list[AnyMessage]) -> str:
    final_document: str = ""
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if (tc["name"] == "write_document_tool") and (tc["args"]["doc_type"] == "final"):
                    final_document = tc["args"]["document"]
                    break

        if final_document:
            break

    assert final_document, f"Final Document Not Found!!!"

    return final_document


def reformat_messages(messages: list[AnyMessage]) -> str:
    result: str = ""

    for msg in messages:
        if isinstance(msg, AIMessage):
            sender: str = "Agent"
        elif isinstance(msg, ToolMessage):
            sender: str = "Tool"
        elif isinstance(msg, HumanMessage):
            sender: str = "Human"
        else:
            sender: str = "Unknown"

        name: str = getattr(msg, "name", "")
        content: str = getattr(msg, "content", "")
        tool_calls: list[dict[str, Any]] = getattr(msg, "tool_calls", [])

        result += f"## `{name}` {sender} Message:\n\n"
        result += f"#### Content:\n{content}\n\n"
        if tool_calls:
            result += f"#### Tool Calls:\n\n"
            for tc in tool_calls:
                result += f"* #### \t Name: `{tc['name']}`\n\n"
                result += f"* #### \t Args:\n\n"
                for arg_name, arg_value in tc['args'].items():
                    result += f"\t\t{arg_name}:\n"
                    result += str(arg_value) + "\n\n"

        result += "\n\n# ********************************\n\n"

    return result


def convert_messages_to_string(messages: list[AnyMessage]) -> str:
    resp: str = "\n-----\n".join([msg.content for msg in messages])
    return resp


def process_event(event: dict[str, Any], chains: dict[str, Any]) -> Any:
    print(event)
    if "tool" in event:
        validation: str = run_validator_chain(
            context_data={
                ""
            },
            response=event["tool"]["messages"][-1].content
        )
        st["messages"].append({"role": "system", "content": validation})
    MESSAGES.append({"role": "system", "content": validation})

    pass



if __name__ == '__main__':
    import os
    import dotenv
    dotenv.load_dotenv("./../../.env")

    model = build_embedding_model("mmd")
    print(model)

    print(model.embed_documents(["Hello World!"]))