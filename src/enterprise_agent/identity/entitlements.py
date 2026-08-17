"""Map roles and raw scopes to agent entitlements.

Replace ROLE_SCOPES with an IdP / admin store later. Deny by default when
neither a known role nor explicit scopes are provided.
"""

from __future__ import annotations

from enterprise_agent.core.config import get_settings
from enterprise_agent.identity.principal import Principal

SHARES_ALL = frozenset(
    {"agent:shares", "agent:shares:quote", "agent:shares:fundamentals"}
)

ROLE_SCOPES: dict[str, frozenset[str]] = {
    "admin": frozenset({"*"}),
    "analyst": SHARES_ALL | frozenset({"agent:weather"}),
    "shares_only": SHARES_ALL,
    "shares_fundamentals_only": frozenset(
        {"agent:shares", "agent:shares:fundamentals"}
    ),
    "weather_only": frozenset({"agent:weather"}),
    "general": frozenset(),
}


def parse_scope_list(raw: str | None) -> frozenset[str]:
    if raw is None:
        return frozenset()
    text = raw.strip()
    if not text:
        return frozenset()
    if text == "*":
        return frozenset({"*"})
    return frozenset(part.strip() for part in text.split(",") if part.strip())


def scopes_for_role(role: str) -> frozenset[str] | None:
    return ROLE_SCOPES.get(role.strip().lower())


def resolve_principal(
    *,
    user_id: str | None = None,
    tenant_id: str | None = None,
    scopes: str | None = None,
    role: str | None = None,
) -> Principal:
    """Build a principal from request headers / CLI flags, falling back to settings."""
    settings = get_settings()
    resolved_role = (role or settings.default_role or "").strip().lower()
    explicit = parse_scope_list(scopes)
    if explicit:
        resolved_scopes = explicit
    elif resolved_role and resolved_role in ROLE_SCOPES:
        resolved_scopes = ROLE_SCOPES[resolved_role]
    else:
        resolved_scopes = parse_scope_list(settings.default_scopes)

    return Principal(
        user_id=(user_id or settings.default_user_id).strip() or settings.default_user_id,
        tenant_id=(tenant_id or settings.default_tenant_id).strip() or settings.default_tenant_id,
        scopes=resolved_scopes,
        roles=frozenset({resolved_role} if resolved_role else ()),
    )
