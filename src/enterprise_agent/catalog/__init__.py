"""Agent catalog: metadata plus build hooks. Supervisor never imports specialists by name."""

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.catalog.registry import allowed_specs, get_spec, list_specs

__all__ = ["AgentSpec", "allowed_specs", "get_spec", "list_specs"]
