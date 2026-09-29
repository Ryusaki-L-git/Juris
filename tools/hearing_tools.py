"""
tools/hearing_tools.py — JURIS Hearing Tools.

Provides read access to LED hearing schedules and next-date information.

Phase 2: Interface + schema only.
Phase 4: execute() connects to LED / Firestore, and optionally eCourts
         for next-date verification (read-only).
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


class GetHearingsTool(JurisTool):
    """
    Retrieve upcoming hearings for a case or across all of the user's cases.
    """

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="get_hearings",
            description=(
                "Retrieve upcoming hearing dates. "
                "If case_id is provided, returns hearings for that case only. "
                "If omitted, returns the next N hearings across all the user's cases. "
                "Results include court name, date, time, and case reference."
            ),
            parameters=[
                ToolParameter(
                    name="case_id",
                    description="Limit hearings to this case. Leave blank for all cases.",
                    required=False,
                    type_hint="string",
                ),
                ToolParameter(
                    name="limit",
                    description="Maximum number of upcoming hearings to return (default 5).",
                    required=False,
                    type_hint="integer",
                    example=5,
                ),
            ],
            resource_type=ResourceType.HEARING,
            action=Action.READ,
        )

    async def execute(self, invocation: ToolInvocation) -> ToolResult:
        return self.error_result(
            "Hearing data access is not yet connected. (Phase 4)"
        )
