"""
tools/case_tools.py — JURIS Case Tools.

Provides JURIS with read access to a user's LED cases.

Phase 2: Defines the tool interface and schema.
Phase 4: execute() connects to LED / Firestore via authorized service.

RULES:
    - The model never directly reads Firestore.
    - Tools return only fields the user is authorized to see.
    - Case data is not cached inside JURIS; it is fetched per-request.
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


class GetCaseTool(JurisTool):
    """
    Retrieve the details of a single LED case by case_id.

    The model may request this tool when the user asks about a specific
    case and the case context (ItemRef) has been provided by LED.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_case",
            description=(
                "Retrieve details for a single LED case. "
                "Requires a valid case_id from the current session context. "
                "Returns case metadata, status, parties, and hearing schedule summary."
            ),
            parameters=[
                ToolParameter(
                    name="case_id",
                    description="The LED case identifier.",
                    required=True,
                    type_hint="string",
                ),
            ],
            resource_type=ResourceType.CASE,
            action=Action.READ,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        # Phase 4: resolve case_id against LED / Firestore.
        # Phase 2: not connected — return not-implemented result.
        return self.error_result(
            "Case data access is not yet connected. (Phase 4)"
        )


class SearchCasesTool(JurisTool):
    """
    Search the user's LED cases by keyword, status, or date range.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_cases",
            description=(
                "Search the user's LED cases. "
                "Supports filtering by keyword, case status, court, or date range. "
                "Returns a list of matching cases with summary fields only."
            ),
            parameters=[
                ToolParameter(
                    name="query",
                    description="Search keyword or natural language query.",
                    required=False,
                    type_hint="string",
                ),
                ToolParameter(
                    name="status",
                    description="Filter by case status (open, closed, adjourned, etc.).",
                    required=False,
                    type_hint="string",
                ),
                ToolParameter(
                    name="limit",
                    description="Maximum number of results to return (default 10).",
                    required=False,
                    type_hint="integer",
                    example=10,
                ),
            ],
            resource_type=ResourceType.CASE,
            action=Action.SEARCH,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "Case search is not yet connected. (Phase 4)"
        )
