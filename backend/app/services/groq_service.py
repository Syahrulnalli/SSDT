"""Server-side Groq chat service used by health checks and future AI workflows."""

from collections.abc import Sequence
from typing import Any

from groq import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AsyncGroq,
    AuthenticationError,
    GroqError,
    RateLimitError,
)

from backend.app.core.config import GROQ_API_KEY, GROQ_MODEL


class GroqServiceError(RuntimeError):
    """A safe, user-facing Groq failure that never includes request secrets."""


async def create_chat_completion(
    messages: Sequence[dict[str, str]],
    *,
    response_format: dict[str, Any] | None = None,
    max_completion_tokens: int | None = None,
) -> str:
    """Send messages to the configured model and return its text response.

    ``response_format`` is kept optional so later SSDT tasks can request
    structured JSON without placing client creation or credentials in routes.
    """
    if not GROQ_API_KEY:
        raise GroqServiceError("GROQ_API_KEY is not configured.")

    request: dict[str, Any] = {
        "model": GROQ_MODEL,
        "messages": list(messages),
    }
    if response_format is not None:
        request["response_format"] = response_format
    if max_completion_tokens is not None:
        request["max_completion_tokens"] = max_completion_tokens

    try:
        async with AsyncGroq(
            api_key=GROQ_API_KEY,
            timeout=10.0,
            max_retries=0,
        ) as client:
            completion = await client.chat.completions.create(**request)
    except AuthenticationError:
        raise GroqServiceError(
            "Groq authentication failed. Check GROQ_API_KEY in the local .env file."
        ) from None
    except RateLimitError:
        raise GroqServiceError("Groq rate limit reached. Try again later.") from None
    except APITimeoutError:
        raise GroqServiceError("The Groq request timed out. Try again later.") from None
    except APIConnectionError:
        raise GroqServiceError("Could not connect to the Groq API.") from None
    except APIStatusError as exc:
        raise GroqServiceError(
            f"Groq returned an error (HTTP {exc.status_code})."
        ) from None
    except GroqError:
        raise GroqServiceError("The Groq request could not be completed.") from None

    if not completion.choices or not completion.choices[0].message.content:
        raise GroqServiceError("The configured Groq model returned no text response.")
    return completion.choices[0].message.content


async def test_groq_connection() -> None:
    """Make one minimal request to verify credentials and model availability."""
    await create_chat_completion(
        [
            {"role": "system", "content": "Reply with OK only."},
            {"role": "user", "content": "Connection check."},
        ],
        # Reasoning models may use a small budget before emitting visible text.
        max_completion_tokens=128,
    )
