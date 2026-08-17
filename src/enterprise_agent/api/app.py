"""Local API + static UI. Same runtime as the CLI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse

from enterprise_agent.api.routers import admin, chat

WEB = Path(__file__).resolve().parents[3] / "web"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_dotenv()
    yield


app = FastAPI(title="Enterprise LangGraph agent", lifespan=lifespan)
app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/")
def chat_page():
    return FileResponse(WEB / "chat.html")


@app.get("/architecture")
def architecture_page():
    return FileResponse(WEB / "architecture.html")


def main() -> None:
    import uvicorn

    uvicorn.run("enterprise_agent.api.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    main()
