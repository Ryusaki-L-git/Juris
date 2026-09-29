"""
tools/document_tools.py — JURIS Document Tools.

Provides access to LED case documents.

LOCAL-FIRST ARCHITECTURE:
    Heavy documents primarily reside on the user's device (LED local storage).
    JURIS does NOT pull full document content from Firestore or cloud storage
    by default.  Instead:

    1. LED sends a structured summary / ItemRef of the document in context.
    2. JURIS works from the summary or metadata.
    3. Full document content is fetched ONLY when the user explicitly
       selects a document for analysis AND the document is accessible
       (cloud-synced copy or user has shared it with JURIS).

    This means get_document_content is a privileged, explicit action —
    not a routine lookup.

Phase 2: Interface + schema only.
Phase 4: execute() resolves document references from LED context.
"""

from __future__ import annotations

from core.permissions import ResourceType, Action
from tools.base import (
    JurisTool,
    ToolDefinition,
    ToolInvocation,
    ToolParameter,
    ToolResult,
)


class GetCaseDocumentsTool(JurisTool):
    """List documents associated with a case (metadata only)."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_case_documents",
            description=(
                "List documents associated with a LED case. "
                "Returns document metadata (name, type, date, size) only. "
                "Does NOT return document content — use get_document_content for that."
            ),
            parameters=[
                ToolParameter(
                    name="case_id",
                    description="The LED case identifier.",
                    required=True,
                    type_hint="string",
                ),
                ToolParameter(
                    name="doc_type",
                    description="Filter by document type (petition, order, affidavit, etc.).",
                    required=False,
                    type_hint="string",
                ),
            ],
            resource_type=ResourceType.DOCUMENT,
            action=Action.READ,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "Document listing is not yet connected. (Phase 4)"
        )


class GetDocumentContentTool(JurisTool):
    """
    Retrieve the content of a specific document for JURIS analysis.

    This is a privileged action — the document must be:
      - cloud-synced OR explicitly shared with JURIS
      - within an authorized case
      - within the user's document permissions

    JURIS must NOT request document content speculatively.
    The model should only request this tool when the user explicitly
    asks JURIS to analyse a document.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_document_content",
            description=(
                "Retrieve the text content of a specific LED document for analysis. "
                "Use ONLY when the user explicitly asks JURIS to read or analyse a document. "
                "Do NOT call this speculatively. "
                "The document must be in the current case context."
            ),
            parameters=[
                ToolParameter(
                    name="document_id",
                    description="The LED document identifier.",
                    required=True,
                    type_hint="string",
                ),
                ToolParameter(
                    name="case_id",
                    description="The case the document belongs to (required for permission check).",
                    required=True,
                    type_hint="string",
                ),
            ],
            resource_type=ResourceType.DOCUMENT,
            action=Action.READ,
            is_write=False,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "Document content access is not yet connected. (Phase 4)"
        )
