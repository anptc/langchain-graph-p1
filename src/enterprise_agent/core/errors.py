"""Typed errors for API and tool policy."""

from __future__ import annotations


class AgentError(Exception):
    """Base application error."""


class ConfigurationError(AgentError):
    """Missing or invalid settings."""


class AccessDenied(AgentError):
    """Principal may not use this agent or tool."""
