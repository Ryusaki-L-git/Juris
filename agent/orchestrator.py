"""
agent/orchestrator.py — JURIS request orchestrator.

The orchestrator is the central authority for a JURIS request.
It is the only component that:
    - Coordinates the pipeline end-to-end
    - Decides which tools are available for this request
    - Calls the permission engine before any tool execution
    - Calls the model gateway
    - Assembles the final ChatResponse

WHAT THE ORCHESTRATOR ENFORCES:
    1. The model never calls tools directly.
    2. Every tool call is permission-checked before execution.
    3. eCourts tools are read-only at the orchestrator level.
    4. Write tools require confirmation (Phase 4 — flagged here).
    5. The model receives only sanitised tool results.

CURRENT PIPELINE (Phase 2):
    ChatRequest + RequestIdentity
        ↓
    ContextResolver  →  RequestContext
        ↓
    [build ModelRequest with available tool definitions]
        ↓
    JurisModelGateway.generate(ModelRequest)
        ↓
    [inspect ModelResponse — tool_calls or direct reply]
        ↓
    [Phase 2: no real tool calls yet — gateway is echo]
        ↓
    ChatResponse assembled and returned to api/chat.py

PHASE 4 ADDITION:
    The gateway may return tool_calls.  The orchestrator will:
        1. Look up each requested tool in the registry.
        2. Check permissions (PermissionEngine.require).
        3. Execute the tool (JurisTool.execute).
        4. Feed results back to the gateway (multi-step loop).
        5. Assemble final response.
"""

from __future__ import annotations

from core.config import settings
from core.identity import RequestIdentity
from gateway.base import JurisModelGateway, ModelRequest
from gateway.factory import get_gateway
from models.chat import ChatRequest, ChatResponse, ResponseStatus
from models.context import RequestContext
from agent.context_resolver import ContextResolver
from tools.base import ToolDefinition
from tools.case_tools import GetCaseTool, SearchCasesTool
from tools.client_tools import GetClientTool, SearchClientsTool
from tools.hearing_tools import GetHearingsTool
from tools.document_tools import GetCaseDocumentsTool, GetDocumentContentTool
from tools.legal_research_tools import SearchIndianLawTool, GetECourtsCaseTool
from tools.controlled_action_tools import (
    DraftDocumentTool,
    CreateReminderTool,
    AskClarificationTool,
)

# ── Tool registry ──────────────────────────────────────────────────────────────
# All tools JURIS knows about.
# The orchestrator selects which subset to expose to the model per request.

_ALL_TOOLS = [
    GetCaseTool(),
    SearchCasesTool(),
    GetClientTool(),
    SearchClientsTool(),
    GetHearingsTool(),
    GetCaseDocumentsTool(),
    GetDocumentContentTool(),
    SearchIndianLawTool(),
    GetECourtsCaseTool(),
    DraftDocumentTool(),
    CreateReminderTool(),
    AskClarificationTool(),
]

_TOOL_REGISTRY: dict[str, object] = {t.definition.name: t for t in _ALL_TOOLS}


def _tool_definitions_as_dicts(
    tools: list[object],
) -> list[dict]:
    """Serialise ToolDefinitions for inclusion in ModelRequest."""
    result = []
    for tool in tools:
        defn: ToolDefinition = tool.definition  # type: ignore[attr-defined]
        result.append({
            "name": defn.name,
            "description": defn.description,
            "parameters": [p.model_dump() for p in defn.parameters],
            "is_ecourts": defn.is_ecourts,
            "is_write": defn.is_write,
        })
    return result


_SYSTEM_PROMPT = """\
You are JURIS, the AI assistant inside Lawyer's E-Diary (LED).

You help Indian lawyers manage their cases, clients, hearings, and documents.

Rules you always follow:
- You only answer questions related to legal case management.
- You do not invent case facts, legal outcomes, or court orders.
- You do not access any data unless a tool is executed and returns it.
- When you lack context, you ask one clarifying question using ask_clarification.
- You never file anything with a court or external system.
- eCourts data is read-only. You never attempt to modify it.
- You are not a search engine. You work within the user's LED data.
"""


class JurisOrchestrator:
    """
    Orchestrates a single JURIS request from receipt to response.

    Stateless — safe to share across requests.
    """

    def __init__(self, gateway: JurisModelGateway | None = None) -> None:
        self._gateway = gateway or get_gateway()
        self._resolver = ContextResolver()

    async def handle(
        self,
        request: ChatRequest,
        identity: RequestIdentity,
    ) -> ChatResponse:
        """
        Process a ChatRequest and return a ChatResponse.

        Phase 2 pipeline:
            1. Resolve context.
            2. Build ModelRequest with all tool definitions.
            3. Call gateway (echo in Phase 2).
            4. Return structured ChatResponse.

        Phase 4 additions:
            - Inspect gateway response for tool_calls.
            - Permission-check and execute each tool.
            - Feed results back to gateway.
            - Loop until finish_reason == "stop".
        """
        # 1. Resolve context
        context: RequestContext = self._resolver.resolve(request, identity)

        # 2. Build the model request
        model_request = ModelRequest(
            system_prompt=_SYSTEM_PROMPT,
            user_message=request.message,
            available_tools=_tool_definitions_as_dicts(_ALL_TOOLS),
            session_id=request.session_id,
            metadata={
                "screen": context.current_screen,
                "has_case": context.active_case is not None,
            },
        )

        # 3. Call the gateway
        model_response = await self._gateway.generate(model_request)

        # 4. Phase 4: handle tool_calls here (not yet implemented).
        #    If the gateway returns tool_calls, the orchestrator will
        #    validate, permission-check, and execute them before re-calling
        #    the gateway.  For now, any tool_calls are logged and ignored.

        # 5. Assemble response
        debug_payload = None
        if settings.debug:
            debug_payload = {
                "gateway": model_response.provider,
                "finish_reason": model_response.finish_reason,
                "screen": context.current_screen,
                "tool_calls_requested": len(model_response.tool_calls),
            }

        return ChatResponse(
            reply=model_response.text,
            status=ResponseStatus.OK,
            session_id=request.session_id,
            debug=debug_payload,
        )
