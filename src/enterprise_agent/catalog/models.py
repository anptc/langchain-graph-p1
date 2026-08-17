"""Catalog entry for one specialist. Add a specialist by exporting an AgentSpec."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from langchain_core.tools import BaseTool


@dataclass(frozen=True)
class AgentSpec:
    id: str
    display_name: str
    description: str
    routing_hint: str
    required_scopes: frozenset[str]
    system_prompt: str
    get_tools: Callable[[], Sequence[BaseTool]]
    get_agent: Callable[[], Any]
    agent_node: str
    tools_node: str
    tool_scopes: dict[str, frozenset[str]] = field(default_factory=dict)

    @property
    def handoff_name(self) -> str:
        return f"transfer_to_{self.id}_agent"
