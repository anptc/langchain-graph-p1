from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from enterprise_agent.api.deps import principal_from_headers
from enterprise_agent.api.serialize import serialize_messages
from enterprise_agent.identity.principal import Principal
from enterprise_agent.orchestration.runtime import invoke_supervisor
from enterprise_agent.persistence.sessions import (
    clear_thread,
    get_messages,
    new_thread_id,
    put_messages,
)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


@router.post("/chat")
async def chat(body: ChatRequest, principal: Principal = Depends(principal_from_headers)):
    text = body.message.strip()
    if not text:
        raise HTTPException(400, "Message is empty.")

    thread_id = body.thread_id or new_thread_id()
    history = get_messages(principal, thread_id)
    history.append(HumanMessage(content=text))
    result = await asyncio.to_thread(invoke_supervisor, principal, history)
    messages = result["messages"]
    put_messages(principal, thread_id, messages)
    return {
        "thread_id": thread_id,
        "principal": {
            "user_id": principal.user_id,
            "tenant_id": principal.tenant_id,
            "scopes": sorted(principal.scopes),
            "roles": sorted(principal.roles),
        },
        "messages": serialize_messages(messages),
    }


@router.post("/reset")
def reset(body: ChatRequest, principal: Principal = Depends(principal_from_headers)):
    thread_id = body.thread_id or new_thread_id()
    new_id = clear_thread(principal, thread_id)
    return {"thread_id": new_id, "messages": []}
