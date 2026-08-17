"""One agent ⇄ tools loop. Specialists supply prompt and tools only."""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition


def compile_react_graph(
    *,
    llm: BaseChatModel,
    tools: Sequence[BaseTool],
    system_prompt: str,
    agent_node: str,
    tools_node: str,
):
    tool_list = list(tools)
    model = llm.bind_tools(tool_list) if tool_list else llm

    def call_model(state: MessagesState):
        messages = [SystemMessage(content=system_prompt), *state["messages"]]
        return {"messages": [model.invoke(messages)]}

    graph = StateGraph(MessagesState)
    graph.add_node(agent_node, call_model)
    graph.add_node(tools_node, ToolNode(tool_list))
    graph.add_edge(START, agent_node)
    graph.add_conditional_edges(
        agent_node,
        tools_condition,
        {"tools": tools_node, END: END},
    )
    graph.add_edge(tools_node, agent_node)
    return graph.compile()
