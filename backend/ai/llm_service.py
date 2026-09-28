"""Gemini REST adapter; API credentials remain exclusively on the backend."""

import httpx

from backend.config import settings


class LLMConfigurationError(Exception):
    """Raised when Gemini credentials are absent."""


class LLMProviderError(Exception):
    """Raised when the configured Gemini provider cannot generate a response."""


def generate_text(prompt: str) -> str:
    """Generate a response through the Gemini API using server-side credentials."""
    if not settings.gemini_api_key:
        raise LLMConfigurationError
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent"
    )
    try:
        response = httpx.post(
            url,
            headers={"x-goog-api-key": settings.gemini_api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("candidates", [])
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        answer = "\n".join(part.get("text", "") for part in parts).strip()
        if not answer:
            raise LLMProviderError("Gemini returned no text response")
        return answer
    except httpx.HTTPError as error:
        raise LLMProviderError("Gemini could not complete the request") from error