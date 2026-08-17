"""Compile and invoke the supervisor for a principal. Graphs cached by allowed agent ids."""

from __future__ import annotations

from enterprise_agent.catalog.registry import allowed_specs
from enterprise_agent.identity.principal import Principal, current_principal
from enterprise_agent.orchestration.supervisor import build_supervisor

_graphs: dict[frozenset[str], object] = {}


def graph_for(principal: Principal):
    allowed = allowed_specs(principal)
    key = frozenset(spec.id for spec in allowed)
    graph = _graphs.get(key)
    if graph is None:
        graph = build_supervisor(allowed)
        _graphs[key] = graph
    return graph


def invoke_supervisor(principal: Principal, messages: list) -> dict:
    token = current_principal.set(principal)
    try:
        return graph_for(principal).invoke({"messages": messages})
    finally:
        current_principal.reset(token)
