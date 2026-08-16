"""Supervisor LangGraph: general tools plus specialist sub-agents.

Stock questions → transfer_to_shares_agent (Alpha Vantage nested graph).
Weather questions → transfer_to_weather_agent (Open-Meteo nested graph).
"""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent.llm import get_llm
from agent.tools import get_tools

SYSTEM_PROMPT = (
    "You are a concise assistant. Use tools when they help. "
    "For stocks, shares, tickers, company fundamentals, share prices, market "
    "movers, or equity news, call transfer_to_shares_agent with a clear task. "
    "Do not invent market numbers. "
    "For weather, forecasts, temperature, rain, wind, or air quality, call "
    "transfer_to_weather_agent with the place name or coordinates. "
    "Do not invent weather numbers. "
    "If a tool is not needed, answer directly."
)


def build_agent():
    llm = get_llm()
    tools = get_tools()
    model = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        response = model.invoke(messages)
        return {"messages": [response]}

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))
    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", tools_condition)
    graph.add_edge("tools", "agent")
    return graph.compile()
