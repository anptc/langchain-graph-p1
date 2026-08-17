from enterprise_agent.identity.entitlements import resolve_principal
from enterprise_agent.orchestration.handoff import make_handoff_tool
from enterprise_agent.specialists.shares.graph import shares_supervisor_prompt
from enterprise_agent.specialists.shares.subcatalog import allowed_nested, nested_specs


def test_shares_only_gets_both_nested_graphs():
    principal = resolve_principal(role="shares_only")
    ids = {spec.id for spec in allowed_nested(principal)}
    assert ids == {"shares_quote", "shares_fundamentals"}


def test_fundamentals_only_role_omits_quote():
    principal = resolve_principal(role="shares_fundamentals_only")
    ids = {spec.id for spec in allowed_nested(principal)}
    assert ids == {"shares_fundamentals"}
    text = shares_supervisor_prompt(allowed_nested(principal))
    assert "transfer_to_shares_fundamentals_agent" in text
    assert "transfer_to_shares_quote_agent" not in text


def test_weather_only_has_no_nested_shares():
    principal = resolve_principal(role="weather_only")
    assert allowed_nested(principal) == ()


def test_admin_wildcard_allows_nested_shares():
    principal = resolve_principal(role="admin")
    ids = {spec.id for spec in allowed_nested(principal)}
    assert ids == {spec.id for spec in nested_specs()}


def test_nested_handoff_names():
    by_id = {spec.id: spec for spec in nested_specs()}
    quote = make_handoff_tool(by_id["shares_quote"])
    fund = make_handoff_tool(by_id["shares_fundamentals"])
    assert quote.name == "transfer_to_shares_quote_agent"
    assert fund.name == "transfer_to_shares_fundamentals_agent"
