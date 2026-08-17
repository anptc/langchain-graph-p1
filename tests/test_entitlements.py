from enterprise_agent.catalog.registry import allowed_specs, list_specs
from enterprise_agent.identity.entitlements import resolve_principal
from enterprise_agent.orchestration.handoff import make_handoff_tool
from enterprise_agent.orchestration.supervisor import supervisor_prompt


def test_admin_sees_all_specialists():
    principal = resolve_principal(role="admin")
    ids = {spec.id for spec in allowed_specs(principal)}
    assert ids == {spec.id for spec in list_specs()}
    assert {"shares", "weather"} <= ids


def test_shares_only_cannot_see_weather():
    principal = resolve_principal(role="shares_only")
    ids = {spec.id for spec in allowed_specs(principal)}
    assert ids == {"shares"}


def test_fundamentals_only_still_sees_parent_shares():
    principal = resolve_principal(role="shares_fundamentals_only")
    assert {spec.id for spec in allowed_specs(principal)} == {"shares"}


def test_weather_only_cannot_see_shares():
    principal = resolve_principal(role="weather_only")
    ids = {spec.id for spec in allowed_specs(principal)}
    assert ids == {"weather"}


def test_general_role_has_no_specialists():
    principal = resolve_principal(role="general")
    assert allowed_specs(principal) == ()


def test_explicit_scopes_override_role():
    principal = resolve_principal(role="admin", scopes="agent:weather")
    assert {spec.id for spec in allowed_specs(principal)} == {"weather"}


def test_supervisor_prompt_omits_denied_agents():
    principal = resolve_principal(role="weather_only")
    allowed = allowed_specs(principal)
    text = supervisor_prompt(allowed)
    assert "transfer_to_weather_agent" in text
    assert "transfer_to_shares_agent" not in text


def test_handoff_name_comes_from_catalog():
    spec = next(s for s in list_specs() if s.id == "shares")
    tool = make_handoff_tool(spec)
    assert tool.name == "transfer_to_shares_agent"
