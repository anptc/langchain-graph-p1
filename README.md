# First LangGraph agent (Gemini 2.5 Flash)

A single LangGraph agent that calls Gemini 2.5 Flash on Vertex AI using
[Application Default Credentials](https://cloud.google.com/docs/authentication/application-default-credentials)
(no API key). The graph is two nodes — `agent` and `tools` — so you can later
add more nodes, subgraphs, and multi-agent routing without rewriting the LLM
setup.

```text
START -> agent --(tool calls?)--> tools -> agent -> ... -> END
                 \--(no tools)--> END
```

## Prerequisites

- Python 3.11+
- A Google Cloud project with billing and the **Vertex AI API** enabled
- [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `GOOGLE_CLOUD_PROJECT` to your GCP project id.

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
python -m agent.main "What is 21 + 21, and what time is it in UTC?"
```

Interactive chat:

```powershell
python -m agent.main
```

Local chat UI (browser):

```powershell
pip install -r requirements.txt
python -m agent.ui
```

Then open http://127.0.0.1:8000 — same graph as the CLI. Architecture page: http://127.0.0.1:8000/architecture

LangChain/LangGraph do not ship a chat UI in the Python packages. LangSmith Studio and Agent Chat UI are separate products (they need a LangGraph Agent Server). This repo’s page is the no-account option.

The parent agent has `get_current_utc_time` and `add_numbers`. Specialists:

- **Shares** — [Alpha Vantage](https://www.alphavantage.co/documentation/). Set `ALPHAVANTAGE_API_KEY` in `.env`. Free-tier is often 5 calls/minute.
- **Weather** — [Open-Meteo](https://open-meteo.com/en/docs) (no API key): geocode, current conditions, daily forecast, air quality.

Examples:

```powershell
python -m agent.main "What is IBM's latest quote and a one-line company overview?"
python -m agent.main "Weather in Bengaluru for the next 3 days, and the air quality."
```

## Project layout

| Path | Role |
|------|------|
| `agent/llm.py` | Gemini 2.5 Flash via Vertex AI + ADC |
| `agent/tools.py` | Tools the agent can call |
| `agent/graph.py` | Parent `StateGraph` (supervisor) |
| `agent/shares.py` | Shares sub-agent graph |
| `agent/shares_tools.py` | Alpha Vantage tools for that sub-agent |
| `agent/alphavantage.py` | Alpha Vantage HTTP client |
| `agent/weather.py` | Weather sub-agent graph |
| `agent/weather_tools.py` | Open-Meteo tools for that sub-agent |
| `agent/openmeteo.py` | Open-Meteo HTTP client (no key) |
| `agent/main.py` | CLI |

## Next steps (multi-node / multi-agent)

Keep `get_llm()` as the shared model factory. Then:

1. **More nodes** — add a `research` or `summarize` node to `StateGraph` and
   route with a conditional edge.
2. **Subagents** — compile a second graph and add it with `graph.add_node("researcher", other_graph)`.
3. **Multi-agent** — add a supervisor node that routes to specialist agents
   (researcher, coder, reviewer) based on the last message.

`create_agent` from `langchain.agents` is the higher-level factory that builds
this same loop. This repo keeps the graph explicit so those later changes stay
visible.
