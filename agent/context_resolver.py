"""
agent/context_resolver.py — Builds the RequestContext for a JURIS request.

Responsibility:
    Take the raw ChatRequest (what LED sent) and the resolved RequestIdentity
    (who is making the request) and produce a validated, enriched RequestContext
    that the orchestrator can work with.

The context resolver is the point where LED's screen/case signals are
translated into JURIS's internal context model.  It does NOT call tools
and does NOT call the model.

Phase 2: Translates directly from ChatRequest → RequestContext.
Phase 4: May enrich context with lightweight metadata from LED (e.g.
         verify that the active_case actually belongs to this user).
"""

from __future__ import annotations

from core.identity import RequestIdentity
from models.chat import ChatRequest
from models.context import RequestContext


class ContextResolver:
    """
    Builds a RequestContext from an incoming ChatRequest + RequestIdentity.

    Stateless — a single instance can handle any number of requests.
    """

    def resolve(
        self,
        request: ChatRequest,
        identity: RequestIdentity,
    ) -> RequestContext:
        """
        Produce a RequestContext for the orchestrator.

        For Phase 2, this is a direct translation: the context LED sends
        in ChatRequest.context is validated by Pydantic on ingestion,
        so we trust it and pass it through.

        Future enrichment (Phase 4):
          - verify active_case belongs to identity.user
          - fetch lightweight case metadata if active_case is set
          - detect context signals (e.g. screen changed since last turn)

        Args:
            request:    The validated ChatRequest from LED.
            identity:   The resolved RequestIdentity (who is calling).

        Returns:
            A RequestContext the orchestrator can use without
            further validation.
        """
        # For Phase 2: pass through the context LED provided.
        # The orchestrator will check permissions before acting on it.
        return request.context
