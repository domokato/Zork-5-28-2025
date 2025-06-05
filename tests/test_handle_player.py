import os
import sys
import types

import pytest
try:
    from langchain.schema import HumanMessage
except Exception:  # pragma: no cover - optional dependency
    class HumanMessage:
        def __init__(self, content: str):
            self.content = content

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Provide a minimal stub for the core module expected by zork_graph
core_stub = types.ModuleType("core")
core_stub.llm = types.SimpleNamespace(invoke=lambda prompt: types.SimpleNamespace(content=""))
sys.modules.setdefault("core", core_stub)

from graph.zork_graph import handle_player


def test_handle_player_with_langchain_messages():
    state = {"messages": [HumanMessage(content="room2")], "current_room": "room1"}
    result = handle_player(state)
    assert result == {"current_room": "room2"}
