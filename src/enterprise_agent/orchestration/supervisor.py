"""Parent StateGraph. Bound tools depend on the principal's allowed specialists."""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.core.llm import get_llm
from enterprise_agent.orchestration.handoff import make_handoff_tool
from enterprise_agent.orchestration.parent_tools import get_general_tools
from enterprise_agent.specialists._base.graph_factory import compile_react_graph
from enterprise_agent.specialists._base.tool_policy import wrap_tools


def supervisor_prompt(specs: tuple[AgentSpec, ...]) -> str:
    parts = ["You are a concise assistant. Use tools when they help."]
    for spec in specs:
        parts.append(
            f"For {spec.routing_hint}, call {spec.handoff_name} with a clear task. "
            "Do not invent those numbers."
        )
    if not specs:
        parts.append(
            "No specialist agents are available for this user. "
            "Use general tools only, or say you cannot retrieve domain data."
        )
    parts.append("If a tool is not needed, answer directly.")
    return " ".join(parts)


def build_supervisor(allowed: tuple[AgentSpec, ...]):
    tools = wrap_tools(get_general_tools(), spec=None)
    tools.extend(make_handoff_tool(spec) for spec in allowed)
    return compile_react_graph(
        llm=get_llm(),
        tools=tools,
        system_prompt=supervisor_prompt(allowed),
        agent_node="agent",
        tools_node="tools",
    )
