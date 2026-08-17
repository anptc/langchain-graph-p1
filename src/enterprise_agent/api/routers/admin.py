from __future__ import annotations

from fastapi import APIRouter, Depends

from enterprise_agent.api.deps import principal_from_headers
from enterprise_agent.catalog.registry import allowed_specs, list_specs
from enterprise_agent.identity.principal import Principal
from enterprise_agent.persistence.audit import recent_events
from enterprise_agent.specialists.shares.subcatalog import allowed_nested, nested_specs

router = APIRouter()


@router.get("/catalog")
def catalog(principal: Principal = Depends(principal_from_headers)):
    allowed = {spec.id for spec in allowed_specs(principal)}
    nested_allowed = {spec.id for spec in allowed_nested(principal)}
    agents = []
    for spec in list_specs():
        entry = {
            "id": spec.id,
            "display_name": spec.display_name,
            "handoff_name": spec.handoff_name,
            "required_scopes": sorted(spec.required_scopes),
            "allowed": spec.id in allowed,
        }
        if spec.id == "shares":
            entry["nested"] = [
                {
                    "id": inner.id,
                    "display_name": inner.display_name,
                    "handoff_name": inner.handoff_name,
                    "required_scopes": sorted(inner.required_scopes),
                    "allowed": inner.id in nested_allowed,
                }
                for inner in nested_specs()
            ]
        agents.append(entry)
    return {"agents": agents}


@router.get("/me")
def me(principal: Principal = Depends(principal_from_headers)):
    return {
        "user_id": principal.user_id,
        "tenant_id": principal.tenant_id,
        "scopes": sorted(principal.scopes),
        "roles": sorted(principal.roles),
        "allowed_agents": [spec.id for spec in allowed_specs(principal)],
        "allowed_nested": [spec.id for spec in allowed_nested(principal)],
    }


@router.get("/audit")
def audit(principal: Principal = Depends(principal_from_headers)):
    events = [
        e
        for e in recent_events(100)
        if e.tenant_id == principal.tenant_id and e.user_id == principal.user_id
    ]
    return {
        "events": [
            {
                "at": e.at,
                "agent_id": e.agent_id,
                "tool_name": e.tool_name,
                "success": e.success,
                "detail": e.detail,
            }
            for e in events
        ]
    }
