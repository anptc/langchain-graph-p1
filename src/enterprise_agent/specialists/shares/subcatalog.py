"""Inner shares graphs. Parent catalog still lists only `shares`."""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.identity.principal import Principal

_NESTED: tuple[AgentSpec, ...] | None = None


def nested_specs() -> tuple[AgentSpec, ...]:
    global _NESTED
    if _NESTED is None:
        from enterprise_agent.specialists.shares.fundamentals.spec import SPEC as fundamentals
        from enterprise_agent.specialists.shares.quote.spec import SPEC as quote

        _NESTED = (quote, fundamentals)
    return _NESTED


def allowed_nested(principal: Principal) -> tuple[AgentSpec, ...]:
    return tuple(spec for spec in nested_specs() if principal.allows(spec.required_scopes))
