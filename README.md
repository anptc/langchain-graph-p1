# Enterprise LangGraph agent (Gemini 2.5 Flash)

A **supervisor + catalogued specialists** agent on Vertex AI using
[Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
(no Gemini API key). The parent graph is still two nodes — `agent` and `tools` —
but specialists are registered in a catalog, and **tools are bound per principal**.
A user who lacks `agent:weather` never sees `transfer_to_weather_agent` in the
model schema.

```text
START -> agent --(tool calls?)--> tools -> agent -> ... -> END
                 \--(no tools)--> END

Specialists (shares, weather, …) run as nested graphs started by
catalog-generated handoff tools. Adding a specialist is a new folder plus
one import in catalog/registry.py — not a new transfer_* function.
```

## Prerequisites

- Python 3.11+
- A Google Cloud project with billing and the **Vertex AI API** enabled
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
copy .env.example .env
```

`pip install -e .` installs the `src/` package (`enterprise_agent`). Edit `.env`
and set `GOOGLE_CLOUD_PROJECT`. For shares, set `ALPHAVANTAGE_API_KEY`.

Log in with Application Default Credentials (user account, local machine):

```powershell
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
gcloud config set project YOUR_PROJECT_ID
```

On Cloud Run / GCE / GKE, skip the login command; the attached service account
is used automatically.

## Run

One-shot:

```powershell
python -m enterprise_agent.apps.cli "What is 21 + 21, and what time is it in UTC?"
```

Interactive chat (all specialists, default `admin` / `*`):

```powershell
python -m enterprise_agent.apps.cli
```

Restrict access (the weather handoff is omitted from the bound tools):

```powershell
python -m enterprise_agent.apps.cli --role shares_only "Weather in Bengaluru?"
python -m enterprise_agent.apps.cli --role shares_fundamentals_only "What is IBM's latest quote?"
python -m enterprise_agent.apps.cli --role shares_fundamentals_only "IBM sector, PE, and a one-line overview"
python -m enterprise_agent.apps.cli --scopes agent:weather "IBM latest quote?"
```

Local chat UI:

```powershell
python -m enterprise_agent.api.app
```

Open http://127.0.0.1:8000 — same runtime as the CLI. Architecture:
http://127.0.0.1:8000/architecture

Use the **access** control on the chat page (or send `X-Role` / `X-Scopes`) to
simulate SSO claims. Production should replace those headers with a verified JWT.

Parent general tools: `get_current_utc_time`, `add_numbers`. Catalogued specialists:

- **Shares** (`agent:shares`) — [Alpha Vantage](https://www.alphavantage.co/documentation/). Nested graphs:
  - **Quote** (`agent:shares:quote`) — latest quote, daily prices, movers, news
  - **Fundamentals** (`agent:shares:fundamentals`) — company overview (sector, PE, EPS, market cap)
- **Weather** (`agent:weather`) — [Open-Meteo](https://open-meteo.com/en/docs) (no API key).

```powershell
python -m enterprise_agent.apps.cli "What is IBM's latest quote and a one-line company overview?"
python -m enterprise_agent.apps.cli "Weather in Bengaluru for the next 3 days, and the air quality."
```

## Access control

Identity is a `Principal` (`user_id`, `tenant_id`, `scopes`, `roles`). It is
injected via a context variable for the duration of `invoke` — never taken from
the user message.

| Layer | What it does |
|--------|----------------|
| API / CLI | Headers (`X-User-Id`, `X-Tenant-Id`, `X-Role`, `X-Scopes`) or `--role` / `--scopes`. Stand-in for OIDC. |
| Entitlements | Named roles (`admin`, `analyst`, `shares_only`, `shares_fundamentals_only`, `weather_only`, `general`) map to scopes. Inner shares graphs use `agent:shares:quote` and `agent:shares:fundamentals`. |
| Bind time | Supervisor is compiled (and cached) for the set of allowed agent ids. Forbidden handoffs are not in the tool schema. |
| Run time | Each specialist tool re-checks scopes and writes an audit event. |

`GET /api/v1/me` and `GET /api/v1/catalog` show the current principal and which
agents they may use. `GET /api/v1/audit` lists that user's recent tool events.

Threads are keyed by **tenant + user + thread_id** so two users cannot share a
session by guessing a UUID.

## Project layout

```text
src/enterprise_agent/
  api/                 FastAPI: headers → principal → runtime
  apps/cli.py          CLI
  catalog/             AgentSpec + registry (add specialists here)
  core/                settings, LLM factory, HTTP helper
  identity/            Principal, roles → scopes
  orchestration/       supervisor, generic handoff, per-principal bind
  persistence/         in-memory threads + audit log
  specialists/
    _base/             shared react-loop factory + tool policy
    shares/            supervisor + quote/ + fundamentals/ + Alpha Vantage client
    weather/           spec, graph, tools, Open-Meteo client
web/                   chat + architecture pages
tests/                 entitlements and tool-policy tests
```

| Path | Role |
|------|------|
| `core/llm.py` | Gemini 2.5 Flash via Vertex AI + ADC |
| `catalog/registry.py` | Loads specialist specs; filters by principal |
| `orchestration/supervisor.py` | Parent `StateGraph` |
| `orchestration/handoff.py` | Generic `transfer_to_<id>_agent` |
| `orchestration/runtime.py` | Graph cached by allowed agent ids |
| `specialists/shares/` | Shares supervisor; nested quote + fundamentals graphs |
| `specialists/weather/` | Weather nested graph + Open-Meteo |
| `identity/` | Principal and entitlements |
| `api/app.py` | HTTP + static UI |

## Add a specialist

1. Create `specialists/<name>/` with `client.py`, `tools.py`, `spec.py` (`AgentSpec`), `graph.py`.
2. Import the spec in `catalog/registry.py`.
3. Assign `required_scopes` (e.g. `agent:research`). Grant that scope via role or IdP later.

Do not add a handoff function to the parent. Do not put FastAPI routes inside a specialist package.

## Tests

```powershell
pip install -e ".[dev]"
pytest
```

These tests do not call Vertex or vendor APIs.

## Next steps

- Replace header identity with OIDC (Entra / Google / Okta) and store entitlements per tenant.
- Swap in-memory sessions for a Postgres LangGraph checkpointer.
- Stream with `astream` so inner tools appear in the UI while they run.
- Optional: `graph.add_node("weather", weather_graph)` if inner messages should live on the parent thread.
