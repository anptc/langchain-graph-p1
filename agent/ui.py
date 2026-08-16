"""Local chat UI for the first LangGraph agent.

LangChain and LangGraph do not ship an end-user app. This FastAPI page talks
to the same compiled graph as `python -m agent.main`.
"""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from pydantic import BaseModel

from agent.graph import build_agent

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"

_agent = None
_sessions: dict[str, list] = {}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global _agent
    load_dotenv()
    _agent = build_agent()
    yield


app = FastAPI(title="LangGraph Gemini agent", lifespan=lifespan)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


def _text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and item.get("text"):
                parts.append(str(item["text"]))
        return "\n".join(parts)
    return str(content)


def serialize_messages(messages: list) -> list[dict]:
    out = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            out.append({"role": "user", "content": _text(msg.content)})
        elif isinstance(msg, ToolMessage):
            out.append(
                {
                    "role": "tool",
                    "name": getattr(msg, "name", "") or "tool",
                    "content": _text(msg.content),
                }
            )
        elif isinstance(msg, AIMessage):
            tool_calls = [
                {
                    "name": call.get("name", ""),
                    "args": call.get("args", {}),
                }
                for call in (msg.tool_calls or [])
            ]
            out.append(
                {
                    "role": "assistant",
                    "content": _text(msg.content),
                    "tool_calls": tool_calls,
                }
            )
    return out


@app.get("/")
def chat_page():
    return FileResponse(DOCS / "chat.html")


@app.get("/architecture")
def architecture_page():
    return FileResponse(DOCS / "architecture.html")


@app.post("/api/chat")
async def chat(body: ChatRequest):
    if _agent is None:
        raise HTTPException(503, "Agent is still starting.")
    text = body.message.strip()
    if not text:
        raise HTTPException(400, "Message is empty.")

    thread_id = body.thread_id or str(uuid4())
    history = list(_sessions.get(thread_id, []))
    history.append(HumanMessage(content=text))
    result = await asyncio.to_thread(_agent.invoke, {"messages": history})
    messages = result["messages"]
    _sessions[thread_id] = messages
    return {"thread_id": thread_id, "messages": serialize_messages(messages)}


@app.post("/api/reset")
def reset(body: ChatRequest):
    thread_id = body.thread_id or str(uuid4())
    _sessions.pop(thread_id, None)
    return {"thread_id": str(uuid4()), "messages": []}


def main() -> None:
    import uvicorn

    uvicorn.run("agent.ui:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
