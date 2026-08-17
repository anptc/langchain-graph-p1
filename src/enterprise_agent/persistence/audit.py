"""Who invoked which agent/tool. Structured log now; persist later."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from enterprise_agent.identity.principal import Principal

logger = logging.getLogger("enterprise_agent.audit")

_events: list["AuditEvent"] = []


@dataclass(frozen=True)
class AuditEvent:
    at: str
    tenant_id: str
    user_id: str
    agent_id: str
    tool_name: str
    success: bool
    detail: str | None = None


def record_audit(
    principal: Principal,
    *,
    agent_id: str,
    tool_name: str,
    success: bool,
    detail: str | None = None,
) -> None:
    event = AuditEvent(
        at=datetime.now(timezone.utc).isoformat(),
        tenant_id=principal.tenant_id,
        user_id=principal.user_id,
        agent_id=agent_id,
        tool_name=tool_name,
        success=success,
        detail=detail,
    )
    _events.append(event)
    logger.info(
        "audit tenant=%s user=%s agent=%s tool=%s success=%s detail=%s",
        event.tenant_id,
        event.user_id,
        event.agent_id,
        event.tool_name,
        event.success,
        event.detail or "",
    )


def recent_events(limit: int = 50) -> list[AuditEvent]:
    return _events[-limit:]
