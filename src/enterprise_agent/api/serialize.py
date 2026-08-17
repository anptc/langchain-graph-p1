from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage


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
