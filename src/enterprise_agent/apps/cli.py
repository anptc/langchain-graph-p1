"""Chat loop for the enterprise LangGraph agent."""

from __future__ import annotations

import argparse

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from enterprise_agent.catalog.registry import allowed_specs
from enterprise_agent.identity.entitlements import resolve_principal
from enterprise_agent.orchestration.runtime import invoke_supervisor


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="Run the enterprise LangGraph Gemini agent.")
    parser.add_argument(
        "prompt",
        nargs="*",
        help="Optional one-shot prompt. Omit for an interactive chat.",
    )
    parser.add_argument("--user", dest="user_id", default=None, help="Principal user id.")
    parser.add_argument("--tenant", dest="tenant_id", default=None, help="Tenant id.")
    parser.add_argument(
        "--role",
        default=None,
        help="Named role: admin, analyst, shares_only, shares_fundamentals_only, weather_only, general.",
    )
    parser.add_argument(
        "--scopes",
        default=None,
        help="Comma-separated scopes (overrides role), e.g. agent:shares or *.",
    )
    args = parser.parse_args()

    principal = resolve_principal(
        user_id=args.user_id,
        tenant_id=args.tenant_id,
        scopes=args.scopes,
        role=args.role,
    )
    allowed = ", ".join(spec.id for spec in allowed_specs(principal)) or "(none)"
    prompt = " ".join(args.prompt).strip()
    if prompt:
        _print_reply(invoke_supervisor(principal, [HumanMessage(content=prompt)]))
        return

    print(
        "Enterprise LangGraph agent (Gemini 2.5 Flash). Type 'quit' to exit.\n"
        f"user={principal.user_id} tenant={principal.tenant_id} "
        f"scopes={sorted(principal.scopes)} specialists={allowed}\n"
    )
    messages = []
    while True:
        user = input("you> ").strip()
        if not user:
            continue
        if user.lower() in {"quit", "exit", "q"}:
            break
        messages.append(HumanMessage(content=user))
        result = invoke_supervisor(principal, messages)
        messages = result["messages"]
        _print_reply(result)


def _print_reply(result: dict) -> None:
    last = result["messages"][-1]
    content = last.content if hasattr(last, "content") else str(last)
    print(f"agent> {content}\n")


if __name__ == "__main__":
    main()
