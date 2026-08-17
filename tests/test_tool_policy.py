from langchain_core.tools import tool

from enterprise_agent.catalog.models import AgentSpec
from enterprise_agent.identity.principal import Principal, current_principal
from enterprise_agent.specialists._base.tool_policy import wrap_tools


@tool
def secret_op() -> str:
    """Should be blocked without scopes."""
    return "leaked"


def test_tool_policy_denies_without_scope():
    spec = AgentSpec(
        id="secret",
        display_name="Secret",
        description="n/a",
        routing_hint="n/a",
        required_scopes=frozenset({"agent:secret"}),
        system_prompt="n/a",
        get_tools=lambda: [secret_op],
        get_agent=lambda: None,
        agent_node="a",
        tools_node="t",
    )
    wrapped = wrap_tools([secret_op], spec)[0]
    principal = Principal(user_id="u", tenant_id="t", scopes=frozenset())
    token = current_principal.set(principal)
    try:
        result = wrapped.invoke({})
    finally:
        current_principal.reset(token)
    assert "Access denied" in result
    assert "leaked" not in result


def test_tool_policy_allows_with_scope():
    spec = AgentSpec(
        id="secret",
        display_name="Secret",
        description="n/a",
        routing_hint="n/a",
        required_scopes=frozenset({"agent:secret"}),
        system_prompt="n/a",
        get_tools=lambda: [secret_op],
        get_agent=lambda: None,
        agent_node="a",
        tools_node="t",
    )
    wrapped = wrap_tools([secret_op], spec)[0]
    principal = Principal(user_id="u", tenant_id="t", scopes=frozenset({"agent:secret"}))
    token = current_principal.set(principal)
    try:
        result = wrapped.invoke({})
    finally:
        current_principal.reset(token)
    assert result == "leaked"
