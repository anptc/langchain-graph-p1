"""Shares supervisor: routes to quote and/or fundamentals nested graphs.

Compiled per principal so denied inner handoffs are not in the tool schema.
"""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.core.llm import get_llm
from enterprise_agent.identity.principal import require_principal
from enterprise_agent.orchestration.handoff import make_handoff_tool
from enterprise_agent.specialists._base.graph_factory import compile_react_graph
from enterprise_agent.specialists.shares.spec import SPEC
from enterprise_agent.specialists.shares.subcatalog import allowed_nested

_graphs: dict[frozenset[str], object] = {}


def shares_supervisor_prompt(nested: tuple[AgentSpec, ...]) -> str:
    parts = [SPEC.system_prompt]
    for spec in nested:
        parts.append(
            f"For {spec.routing_hint}, call {spec.handoff_name} with a clear task."
        )
    if not nested:
        parts.append("No nested shares specialists are available for this user.")
    return " ".join(parts)


def build_shares_agent(nested: tuple[AgentSpec, ...]):
    tools = [make_handoff_tool(spec) for spec in nested]
    return compile_react_graph(
        llm=get_llm(),
        tools=tools,
        system_prompt=shares_supervisor_prompt(nested),
        agent_node=SPEC.agent_node,
        tools_node=SPEC.tools_node,
    )


def get_shares_agent():
    principal = require_principal()
    nested = allowed_nested(principal)
    key = frozenset(spec.id for spec in nested)
    graph = _graphs.get(key)
    if graph is None:
        graph = build_shares_agent(nested)
        _graphs[key] = graph
    return graph
