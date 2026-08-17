"""Authenticated caller. Never take tenant or scopes from the model."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    user_id: str
    tenant_id: str
    scopes: frozenset[str]
    roles: frozenset[str] = frozenset()

    def allows(self, required: frozenset[str] | set[str]) -> bool:
        if not required:
            return True
        if "*" in self.scopes:
            return True
        return set(required) <= set(self.scopes)


current_principal: ContextVar[Principal | None] = ContextVar(
    "current_principal", default=None
)


def require_principal() -> Principal:
    principal = current_principal.get()
    if principal is None:
        raise RuntimeError("No principal bound for this invoke. Set current_principal.")
    return principal
