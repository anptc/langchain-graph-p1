"""Resolve Principal from headers. Replace with OIDC later."""

from __future__ import annotations

from fastapi import Header

from enterprise_agent.identity.entitlements import resolve_principal
from enterprise_agent.identity.principal import Principal


def principal_from_headers(
    x_user_id: str | None = Header(default=None, alias="X-User-Id"),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
    x_scopes: str | None = Header(default=None, alias="X-Scopes"),
    x_role: str | None = Header(default=None, alias="X-Role"),
) -> Principal:
    return resolve_principal(
        user_id=x_user_id,
        tenant_id=x_tenant_id,
        scopes=x_scopes,
        role=x_role,
    )
