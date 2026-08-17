"""Explicit specialist list. One new import here when you add a specialist folder."""

from __future__ import annotations

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.identity.principal import Principal

_SPECS: tuple[AgentSpec, ...] | None = None


def _load() -> tuple[AgentSpec, ...]:
    global _SPECS
    if _SPECS is None:
        from enterprise_agent.specialists.shares.spec import SPEC as shares
        from enterprise_agent.specialists.weather.spec import SPEC as weather

        _SPECS = (shares, weather)
        ids = [spec.id for spec in _SPECS]
        if len(ids) != len(set(ids)):
            raise RuntimeError(f"Duplicate specialist ids: {ids}")
    return _SPECS


def list_specs() -> tuple[AgentSpec, ...]:
    return _load()


def get_spec(agent_id: str) -> AgentSpec:
    for spec in _load():
        if spec.id == agent_id:
            return spec
    raise KeyError(agent_id)


def allowed_specs(principal: Principal) -> tuple[AgentSpec, ...]:
    return tuple(spec for spec in _load() if principal.allows(spec.required_scopes))
