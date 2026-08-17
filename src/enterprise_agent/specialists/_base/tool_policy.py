"""Wrap tools: deny-by-default scopes plus audit. Reads Principal from contextvar."""

from __future__ import annotations

from collections.abc import Sequence

from langchain_core.tools import BaseTool, StructuredTool

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.identity.principal import require_principal
from enterprise_agent.persistence.audit import record_audit


def wrap_tools(tools: Sequence[BaseTool], spec: AgentSpec | None = None) -> list[BaseTool]:
    return [_wrap_one(tool, spec) for tool in tools]


def _wrap_one(tool: BaseTool, spec: AgentSpec | None) -> BaseTool:
    required = spec.required_scopes if spec else frozenset()
    if spec and tool.name in spec.tool_scopes:
        required = spec.tool_scopes[tool.name]
    agent_id = spec.id if spec else "parent"

    def _run(*args, **kwargs):
        principal = require_principal()
        if not principal.allows(required):
            record_audit(
                principal,
                agent_id=agent_id,
                tool_name=tool.name,
                success=False,
                detail="access_denied",
            )
            return (
                f"Access denied: principal {principal.user_id} lacks scopes "
                f"{sorted(required)} for tool {tool.name}."
            )
        try:
            result = tool.invoke(kwargs if kwargs else (args[0] if args else {}))
            record_audit(principal, agent_id=agent_id, tool_name=tool.name, success=True)
            return result
        except Exception as exc:
            record_audit(
                principal,
                agent_id=agent_id,
                tool_name=tool.name,
                success=False,
                detail=type(exc).__name__,
            )
            raise

    return StructuredTool.from_function(
        func=_run,
        name=tool.name,
        description=tool.description,
        args_schema=tool.args_schema,
    )
