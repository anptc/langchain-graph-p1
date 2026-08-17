"""In-memory threads keyed by tenant + user + thread. Not shared across processes."""

from __future__ import annotations

from uuid import uuid4

from enterprise_agent.identity.principal import Principal

_sessions: dict[tuple[str, str, str], list] = {}


def new_thread_id() -> str:
    return str(uuid4())


def get_messages(principal: Principal, thread_id: str) -> list:
    return list(_sessions.get((principal.tenant_id, principal.user_id, thread_id), []))


def put_messages(principal: Principal, thread_id: str, messages: list) -> None:
    _sessions[(principal.tenant_id, principal.user_id, thread_id)] = list(messages)


def clear_thread(principal: Principal, thread_id: str) -> str:
    _sessions.pop((principal.tenant_id, principal.user_id, thread_id), None)
    return new_thread_id()
