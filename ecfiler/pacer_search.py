"""PACER Case Locator API client.

Uses the PCL REST API to search for and retrieve case information.
Docs: https://pacer.uscourts.gov/help/pacer/pacer-case-locator-pcl-api-user-guide
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

PCL_API_URL = "https://pcl.uscourts.gov/pcl-public-api/rest"
PCL_QA_URL = "https://qa-pcl.uscourts.gov/pcl-public-api/rest"


@dataclass
class CaseResult:
    """A case found via PACER Case Locator."""

    case_number: str
    case_title: str
    court_id: str
    court_name: str
    date_filed: str
    date_closed: str
    judge: str
    case_type: str  # cv, cr, bk, etc.

    @property
    def is_open(self) -> bool:
        return not self.date_closed

    @property
    def display(self) -> str:
        status = "Open" if self.is_open else f"Closed {self.date_closed}"
        parts = [self.case_title]
        if self.judge:
            parts.append(f"Judge {self.judge}")
        parts.append(status)
        return " | ".join(parts)


class PacerSearchError(Exception):
    """Raised when PACER case search fails."""


class PacerSearch:
    """Client for the PACER Case Locator API."""

    def __init__(self, auth_token: str, use_qa: bool = False) -> None:
        self.auth_token = auth_token
        self.base_url = PCL_QA_URL if use_qa else PCL_API_URL
        self._client = httpx.Client(timeout=30.0)

    def search_by_case_number(
        self,
        case_number: str,
        court_id: str | None = None,
    ) -> list[CaseResult]:
        """Search for a case by case number.

        Args:
            case_number: Full or partial case number
            court_id: Optional court ID to narrow search

        Returns:
            List of matching cases
        """
        params: dict[str, str] = {
            "caseNumberFull": case_number,
        }
        if court_id:
            params["courtId"] = court_id

        return self._search("cases", params)

    def search_by_party(
        self,
        party_name: str,
        court_id: str | None = None,
        case_type: str | None = None,
    ) -> list[CaseResult]:
        """Search for cases by party name.

        Args:
            party_name: Party last name or organization name
            court_id: Optional court filter
            case_type: Optional type filter (cv, cr, bk)

        Returns:
            List of matching cases
        """
        params: dict[str, str] = {
            "lastName": party_name,
        }
        if court_id:
            params["courtId"] = court_id
        if case_type:
            params["caseType"] = case_type

        return self._search("parties", params)

    def get_case(self, court_id: str, case_number: str) -> CaseResult | None:
        """Get a specific case by court and case number.

        Returns None if not found.
        """
        results = self.search_by_case_number(case_number, court_id)
        # Return exact match if found
        for r in results:
            if r.case_number == case_number and r.court_id == court_id:
                return r
        return results[0] if results else None

    def _search(self, endpoint: str, params: dict[str, str]) -> list[CaseResult]:
        """Execute a PCL API search."""
        try:
            response = self._client.get(
                f"{self.base_url}/{endpoint}",
                params=params,
                headers={
                    "Accept": "application/json",
                    "X-NEXT-GEN-CSO": self.auth_token,
                },
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise PacerSearchError("PACER authentication expired. Re-authenticate.") from e
            raise PacerSearchError(f"PACER search failed: {e}") from e
        except httpx.RequestError as e:
            raise PacerSearchError(f"Cannot reach PACER: {e}") from e

        data = response.json()
        content = data.get("content", [])

        return [
            CaseResult(
                case_number=item.get("caseNumberFull", ""),
                case_title=item.get("caseTitle", ""),
                court_id=item.get("courtId", ""),
                court_name=item.get("courtName", ""),
                date_filed=item.get("dateFiled", ""),
                date_closed=item.get("dateClosed", ""),
                judge=item.get("assignedTo", ""),
                case_type=item.get("caseType", ""),
            )
            for item in content
        ]

    def close(self) -> None:
        self._client.close()
