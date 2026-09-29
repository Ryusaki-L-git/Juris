"""
tools/client_tools.py — JURIS Client Tools.

Provides read access to LED client profiles.

Client data is sensitive personal information.  These tools must only
return fields the authenticated user is authorized to view (enforced
by the permission engine before execute() is called).

Phase 2: Interface + schema only.
Phase 4: execute() connects to LED / Firestore.
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


class GetClientTool(JurisTool):
    """Retrieve details for a single LED client by client_id."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_client",
            description=(
                "Retrieve profile details for a single LED client. "
                "Returns name, contact information, and associated case IDs. "
                "Sensitive fields are filtered by the permission layer."
            ),
            parameters=[
                ToolParameter(
                    name="client_id",
                    description="The LED client identifier.",
                    required=True,
                    type_hint="string",
                ),
            ],
            resource_type=ResourceType.CLIENT,
            action=Action.READ,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "Client data access is not yet connected. (Phase 4)"
        )


class SearchClientsTool(JurisTool):
    """Search the user's LED client list."""

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_clients",
            description=(
                "Search LED clients by name or contact details. "
                "Returns summary records only (no full profile)."
            ),
            parameters=[
                ToolParameter(
                    name="query",
                    description="Name or contact keyword to search.",
                    required=True,
                    type_hint="string",
                ),
                ToolParameter(
                    name="limit",
                    description="Maximum results (default 10).",
                    required=False,
                    type_hint="integer",
                    example=10,
                ),
            ],
            resource_type=ResourceType.CLIENT,
            action=Action.SEARCH,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "Client search is not yet connected. (Phase 4)"
        )
