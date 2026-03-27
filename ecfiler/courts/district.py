"""District court-specific CM/ECF workflow overrides."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ecfiler.courts.base import BaseCourt

if TYPE_CHECKING:
    from playwright.sync_api import Page


class DistrictCourt(BaseCourt):
    """US District Court CM/ECF workflow.

    Standard NextGen workflow with minimal overrides.
    District courts are the most standardized across the federal system.
    """

    def navigate_to_filing(self, page: Page) -> None:
        """District courts use the standard filing URL."""
        url = f"{self.profile.ecf_url}/cgi-bin/iquery.pl"
        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Some district courts have an interstitial consent page
        if "requires_consent" in self.profile.quirks:
            consent_btn = page.query_selector(
                "input[value='Continue'], button:has-text('I Accept')"
            )
            if consent_btn:
                consent_btn.click()
                page.wait_for_load_state("networkidle")

    def get_docket_entries(self, page: Page, case_number: str) -> list[dict[str, str]]:
        """Fetch recent docket entries for the case (for related filing selection).

        Returns list of {"number": "45", "text": "Motion to Dismiss", "date": "2024-11-15"}
        """
        entries: list[dict[str, str]] = []

        rows = page.query_selector_all("table tr")
        for row in rows:
            cells = row.query_selector_all("td")
            if len(cells) >= 3:
                number = cells[0].inner_text().strip()
                date = cells[1].inner_text().strip()
                text = cells[2].inner_text().strip()
                if number.isdigit():
                    entries.append({
                        "number": number,
                        "date": date,
                        "text": text[:100],
                    })

        return entries
