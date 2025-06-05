import os
import sqlite3
from typing import Annotated, TypedDict, List, Dict

try:
    from langchain.schema import HumanMessage
except Exception:  # pragma: no cover - optional dependency
    class HumanMessage:
        """Fallback HumanMessage with just a content attribute."""

        def __init__(self, content: str):
            self.content = content

from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages

import core

DB_PATH = os.path.join(os.path.dirname(__file__), "../db/rooms.db")


def get_room_description(room_id: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT description FROM rooms WHERE id=?", (room_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""


class GameState(TypedDict):
    messages: Annotated[List[Dict], add_messages]
    current_room: str


graph_builder = StateGraph(GameState)


def summarize_room(state: GameState):
    desc = get_room_description(state["current_room"])
    prompt = f"Summarize this room for the player and ask what they want to do:\n{desc}"
    summary = core.llm.invoke(prompt).content
    return {
        "messages": [{"role": "assistant", "content": summary}],
    }


def handle_player(state: GameState):
    messages = state["messages"]
    content = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            content = msg.content
            break
    else:
        last_msg = messages[-1]
        content = getattr(last_msg, "content", "")
    lower = content.lower()
    if "detail" in lower:
        desc = get_room_description(state["current_room"])
        prompt = f"Add some extra details about this room:\n{desc}"
        extra = core.llm.invoke(prompt).content
        return {"messages": [{"role": "assistant", "content": extra}]}
    elif "room2" in lower:
        return {"current_room": "room2"}
    elif "room1" in lower:
        return {"current_room": "room1"}
    else:
        return {"messages": [{"role": "assistant", "content": "I don't understand."}]}


graph_builder.add_node("describe", summarize_room)
graph_builder.add_node("action", handle_player)

graph_builder.add_edge("describe", "action")
graph_builder.add_edge("action", "describe")

graph_builder.set_entry_point("action")

graph = graph_builder.compile()
graph.interrupt_after_nodes = ["describe"]
