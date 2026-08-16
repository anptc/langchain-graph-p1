"""Shares sub-agent graph. Tools live in shares_tools.py; the parent handoff lives in tools.py."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent.llm import get_llm
from agent.shares_tools import get_shares_tools

SHARES_PROMPT = (
    "You are a shares research specialist. Use Alpha Vantage tools for quotes, "
    "company facts, daily prices, ticker search, news, and market movers. "
    "Prefer a ticker (e.g. IBM, AAPL). If the user gives a company name, search first. "
    "Summarize numbers clearly. If the API returns Note/Information (rate limit), say so. "
    "This is market data, not financial advice."
)

_shares_graph = None


def build_shares_agent():
    llm = get_llm()
    tools = get_shares_tools()
    model = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        messages = [SystemMessage(content=SHARES_PROMPT), *state["messages"]]
        return {"messages": [model.invoke(messages)]}

    graph = StateGraph(MessagesState)
    graph.add_node("shares_agent", call_model)
    graph.add_node("shares_tools", ToolNode(tools))
    graph.add_edge(START, "shares_agent")
    graph.add_conditional_edges(
        "shares_agent",
        tools_condition,
        {"tools": "shares_tools", END: END},
    )
    graph.add_edge("shares_tools", "shares_agent")
    return graph.compile()


def get_shares_agent():
    global _shares_graph
    if _shares_graph is None:
        _shares_graph = build_shares_agent()
    return _shares_graph
