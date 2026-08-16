"""Chat loop for the first LangGraph agent."""

from __future__ import annotations

import argparse

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from agent.graph import build_agent


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the first LangGraph Gemini agent.")
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Optional one-shot prompt. Omit for an interactive chat.",
    )
    args = parser.parse_args()

    agent = build_agent()
    prompt = " ".join(args.prompt).strip()
    if prompt:
        _print_reply(agent.invoke({"messages": [HumanMessage(content=prompt)]}))
        return

    print("First LangGraph agent (Gemini 2.5 Flash). Type 'quit' to exit.\n")
    messages = []
    while True:
        user = input("you> ").strip()
        if not user:
            continue
        if user.lower() in {"quit", "exit", "q"}:
            break
        messages.append(HumanMessage(content=user))
        result = agent.invoke({"messages": messages})
        messages = result["messages"]
        _print_reply(result)


def _print_reply(result: dict) -> None:
    last = result["messages"][-1]
    content = last.content if hasattr(last, "content") else str(last)
    print(f"agent> {content}\n")


if __name__ == "__main__":
    main()
