"""Weather sub-agent graph. Tools live in weather_tools.py; the parent handoff lives in tools.py."""

from __future__ import annotations

from langchain_core.messages import SystemMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from agent.llm import get_llm
from agent.weather_tools import get_weather_tools

WEATHER_PROMPT = (
    "You are a weather specialist. Use Open-Meteo tools only. "
    "If the user gives a city or place name, geocode it first, then call weather "
    "or air-quality with that latitude and longitude. "
    "Summarize in the place's local timezone. Temperatures are Celsius unless asked otherwise. "
    "This is a forecast, not a warning service."
)

_weather_graph = None


def build_weather_agent():
    llm = get_llm()
    tools = get_weather_tools()
    model = llm.bind_tools(tools)

    def call_model(state: MessagesState):
        messages = [SystemMessage(content=WEATHER_PROMPT), *state["messages"]]
        return {"messages": [model.invoke(messages)]}

    graph = StateGraph(MessagesState)
    graph.add_node("weather_agent", call_model)
    graph.add_node("weather_tools", ToolNode(tools))
    graph.add_edge(START, "weather_agent")
    graph.add_conditional_edges(
        "weather_agent",
        tools_condition,
        {"tools": "weather_tools", END: END},
    )
    graph.add_edge("weather_tools", "weather_agent")
    return graph.compile()


def get_weather_agent():
    global _weather_graph
    if _weather_graph is None:
        _weather_graph = build_weather_agent()
    return _weather_graph
