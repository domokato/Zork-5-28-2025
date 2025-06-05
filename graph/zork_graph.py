from typing import Annotated, Any
from typing_extensions import TypedDict

from langchain.schema import HumanMessage, AIMessage, BaseMessage
from langgraph.graph.message import add_messages


class GameState(TypedDict):
    """State used by the Zork graph."""

    messages: Annotated[list[Any], add_messages]


def handle_player(state: GameState) -> dict:
    """Process the latest player message.

    The incoming state contains a list of messages which may be dictionaries
    or LangChain ``BaseMessage`` instances. Historically this function treated
    the last item as a dictionary, but LangChain messages expose the text as
    the ``content`` attribute. To work with both formats we inspect the object
    and fall back to ``getattr``.
    """

    messages = state["messages"]
    # Walk messages in reverse to find the most recent user message if present
    last_msg: Any | None = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_msg = msg
            break
    if last_msg is None:
        last_msg = messages[-1]

    content = getattr(last_msg, "content", "")
    if not content and isinstance(last_msg, dict):
        content = last_msg.get("content", "")

    # For now simply echo the content back as the AI response
    reply = AIMessage(content=f"You said: {content}")
    return {"messages": [reply]}
