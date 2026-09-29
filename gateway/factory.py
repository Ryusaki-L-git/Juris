"""
gateway/factory.py — JURIS Model Gateway factory.

The orchestrator calls get_gateway() to obtain the active gateway.
The selection is driven entirely by settings.gateway (JURIS_GATEWAY env var).

Adding a new provider:
    1. Implement JurisModelGateway in a new file (e.g. gemini_gateway.py).
    2. Add its name to the import block and the match statement below.
    3. Update the Literal type in core/config.py.
    4. Set JURIS_GATEWAY=<name> in .env.
    No other files need to change.
"""

from __future__ import annotations

from functools import lru_cache

from core.config import settings
from gateway.base import JurisModelGateway


@lru_cache(maxsize=1)
def get_gateway() -> JurisModelGateway:
    """
    Return the singleton gateway instance for the current configuration.

    lru_cache means the gateway is constructed once per process.
    Call get_gateway.cache_clear() in tests to reset between test cases.
    """
    match settings.gateway:
        case "echo":
            from gateway.echo_gateway import EchoGateway
            return EchoGateway()
        case _:
            # Defensive: should never reach here because Settings validates
            # the gateway value, but fail loudly if it does.
            raise ValueError(
                f"Unknown JURIS_GATEWAY value: '{settings.gateway}'. "
                "Check your .env file and core/config.py."
            )
