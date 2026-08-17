"""Generic specialist handoff. One factory — no per-agent transfer_* functions."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_core.tools import StructuredTool

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.identity.principal import require_principal
from enterprise_agent.persistence.audit import record_audit


def _text(content) -> str:
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts) or str(content)
    return str(content or "")


def make_handoff_tool(spec: AgentSpec) -> StructuredTool:
    def transfer(task: str) -> str:
        principal = require_principal()
        if not principal.allows(spec.required_scopes):
            record_audit(
                principal,
                agent_id=spec.id,
                tool_name=spec.handoff_name,
                success=False,
                detail="access_denied",
            )
            return (
                f"Access denied: this user cannot use the {spec.display_name} agent "
                f"(requires {sorted(spec.required_scopes)})."
            )
        record_audit(principal, agent_id=spec.id, tool_name=spec.handoff_name, success=True)
        result = spec.get_agent().invoke({"messages": [HumanMessage(content=task)]})
        last = result["messages"][-1]
        return _text(getattr(last, "content", last))

    return StructuredTool.from_function(
        func=transfer,
        name=spec.handoff_name,
        description=spec.description,
    )
