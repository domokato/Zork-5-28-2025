from langchain.schema import HumanMessage

import graph.zork_graph as zg


def test_handle_player_with_langchain_message():
    state = {"messages": [HumanMessage(content="look around")]} 
    try:
        result = zg.handle_player(state)
    except TypeError as exc:
        raise AssertionError(f"TypeError raised: {exc}")
    assert isinstance(result, dict)
    assert result["messages"][0].content.startswith("You said:")
