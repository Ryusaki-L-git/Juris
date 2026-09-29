"""
tools/legal_research_tools.py — JURIS Legal Research Tools.

Provides read-only access to Indian law and eCourts data.

CRITICAL ECOURTS RULE:
    eCourts data is READ-ONLY.
    JURIS must NEVER attempt to write, file, or modify anything in eCourts.
    This rule is enforced at multiple levels:
      1. This tool is marked is_ecourts=True in its ToolDefinition.
      2. The orchestrator enforces read-only for all is_ecourts tools.
      3. The HTTP client (Phase 4) will be configured with no write methods.

Phase 2: Interface + schema only.
Phase 4: execute() connects to eCourts API (read-only) and legal DB.
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


class SearchIndianLawTool(JurisTool):
    """
    Search Indian statutes, sections, and legal provisions.

    Source: Legal database (to be determined in Phase 4).
    Read-only.  Never modifies any external system.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_indian_law",
            description=(
                "Search Indian statutes, acts, sections, and legal provisions. "
                "Returns relevant legal text and citations. "
                "Use when the user asks about a specific law, section, or provision."
            ),
            parameters=[
                ToolParameter(
                    name="query",
                    description="The legal query (e.g. 'Section 138 NI Act', 'IPC 420').",
                    required=True,
                    type_hint="string",
                ),
                ToolParameter(
                    name="act",
                    description="Narrow to a specific Act (e.g. 'IPC', 'CrPC', 'NI Act').",
                    required=False,
                    type_hint="string",
                ),
            ],
            resource_type=ResourceType.LEGAL_RESEARCH,
            action=Action.SEARCH,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "Legal research is not yet connected. (Phase 4)"
        )


class GetECourtsCaseTool(JurisTool):
    """
    Fetch case status from the eCourts portal (read-only).

    NEVER writes to eCourts.
    NEVER modifies case records.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_ecourts_case",
            description=(
                "Retrieve case status and next hearing date from eCourts (read-only). "
                "Requires a CNR number. "
                "This tool NEVER modifies eCourts data."
            ),
            parameters=[
                ToolParameter(
                    name="cnr_number",
                    description="The Case Number Record (CNR) from eCourts.",
                    required=True,
                    type_hint="string",
                    example="MHCC010012342024",
                ),
            ],
            resource_type=ResourceType.ECOURTS,
            action=Action.READ,
            is_ecourts=True,    # orchestrator enforces read-only for this flag
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "eCourts integration is not yet connected. (Phase 4)"
        )
