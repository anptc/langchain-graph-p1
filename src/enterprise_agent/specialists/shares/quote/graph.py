"""Compiled quote nested graph."""

from __future__ import annotations

from enterprise_agent.core.llm import get_llm
from enterprise_agent.specialists._base.graph_factory import compile_react_graph
from enterprise_agent.specialists._base.tool_policy import wrap_tools
from enterprise_agent.specialists.shares.quote.spec import SPEC

_graph = None


def build_quote_agent():
    tools = wrap_tools(SPEC.get_tools(), SPEC)
    return compile_react_graph(
        llm=get_llm(),
        tools=tools,
        system_prompt=SPEC.system_prompt,
        agent_node=SPEC.agent_node,
        tools_node=SPEC.tools_node,
    )


def get_quote_agent():
    global _graph
    if _graph is None:
        _graph = build_quote_agent()
    return _graph
