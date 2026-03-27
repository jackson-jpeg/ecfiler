"""Appellate court-specific CM/ECF workflow overrides."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ecfiler.courts.base import BaseCourt

if TYPE_CHECKING:
    from playwright.sync_api import Page


class AppellateCourt(BaseCourt):
    """US Circuit Court of Appeals CM/ECF workflow.

    Appellate courts have a fundamentally different filing interface:
    - Different document types (briefs, appendices, petitions for review)
    - Page limit enforcement
    - Certificate of compliance requirements
    - Different event code taxonomy
    - No case number input — uses docket number format (XX-XXXX)
    """

    def navigate_to_filing(self, page: Page) -> None:
        """Appellate CM/ECF uses a different URL pattern."""
        url = f"{self.profile.ecf_url}/n/beam/servlet/TransportRoom"
        page.goto(url)
        page.wait_for_load_state("networkidle")

    def enter_case_number(self, page: Page, case_number: str) -> None:
        """Appellate cases use docket number format: XX-XXXX.

        Converts district-style numbers if needed.
        """
        # Appellate case number input
        page.fill(
            "input[name='caseNum'], input[name='case_number'], #caseNum",
            case_number,
        )
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

    def select_event_category(self, page: Page, category: str) -> None:
        """Appellate courts have different event categories.

        Typical: Briefs, Motions, Petitions, Notices, Correspondence
        """
        page.select_option(
            self.selectors.event_category_dropdown,
            label=category,
        )
        page.wait_for_load_state("networkidle")

    def set_page_count(self, page: Page, count: int) -> None:
        """Set the document page count (required for briefs)."""
        page_input = page.query_selector(
            "input[name='pageCount'], input[name='page_count']"
        )
        if page_input:
            page_input.fill(str(count))

    def set_word_count(self, page: Page, count: int) -> None:
        """Set the document word count (required for briefs)."""
        word_input = page.query_selector(
            "input[name='wordCount'], input[name='word_count']"
        )
        if word_input:
            word_input.fill(str(count))

    def select_filing_type(self, page: Page, filing_type: str) -> None:
        """Select appellate filing type (opening brief, reply brief, etc.)."""
        page.select_option(
            "select[name='filingType'], #filing_type",
            label=filing_type,
        )
        page.wait_for_load_state("networkidle")

    def check_certificate_of_compliance(self, page: Page) -> None:
        """Check the certificate of compliance checkbox if present."""
        cert_checkbox = page.query_selector(
            "input[name='certCompliance'], input[name='cert_compliance']"
        )
        if cert_checkbox:
            cert_checkbox.check()
