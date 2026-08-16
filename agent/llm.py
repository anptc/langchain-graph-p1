"""Gemini chat model on Vertex AI generateContent (ADC, not Agent Platform)."""

from __future__ import annotations

import os

from google.auth import default as google_auth_default
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm() -> ChatGoogleGenerativeAI:
    """Call Gemini 2.5 Flash via Vertex AI model API using ADC.

    GOOGLE_GENAI_USE_VERTEXAI=true + vertexai=True send traffic to Vertex
    generateContent, not the Gemini Developer API / Agent Platform client.
    """
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "true"

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    credentials, detected_project = google_auth_default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    project = project or detected_project
    if not project:
        raise RuntimeError(
            "No Google Cloud project found. Set GOOGLE_CLOUD_PROJECT or run "
            "`gcloud auth application-default set-quota-project YOUR_PROJECT_ID`."
        )

    return ChatGoogleGenerativeAI(
        model=model,
        vertexai=True,
        project=project,
        location=location,
        credentials=credentials,
        temperature=0.2,
    )
