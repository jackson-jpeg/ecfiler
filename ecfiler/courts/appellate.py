"""Appellate court-specific CM/ECF workflow overrides."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ecfiler.courts.base import BaseCourt, ECFFormError
from ecfiler.logging import get_logger

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = get_logger(__name__)


class AppellateCourt(BaseCourt):
    """US Circuit Court of Appeals CM/ECF workflow.

    Appellate courts have a fundamentally different filing interface:
    - Different document types (briefs, appendices, petitions for review)
    - Page/word count requirements (MUST be provided for briefs)
    - Certificate of compliance requirements
    - Different event code taxonomy
    - Different URL patterns
    - Docket number format: XX-XXXX (not district-style)
    """

    def navigate_to_filing(self, page: Page) -> None:
        """Appellate CM/ECF uses a different URL pattern."""
        url = f"{self.profile.ecf_url}/n/beam/servlet/TransportRoom"
        page.goto(url)
        page.wait_for_load_state("networkidle")

    def enter_case_number(self, page: Page, case_number: str) -> None:
        """Appellate cases use docket number format: XX-XXXX."""
        for selector in [
            "input[name='caseNum']",
            "input[name='case_number']",
            "#caseNum",
            self.selectors.case_number_input,
        ]:
            el = page.query_selector(selector)
            if el:
                page.fill(selector, case_number)
                page.keyboard.press("Enter")
                page.wait_for_load_state("networkidle")
                logger.info("Entered appellate case number: %s", case_number)

                error = self._detect_page_error(page)
                if error:
                    raise ECFFormError(f"Case lookup failed: {error}")
                return

        raise ECFFormError("Case number input not found on appellate filing page")

    def select_event_category(self, page: Page, category: str) -> None:
        """Appellate courts have different event categories.

        Typical: Briefs, Motions, Petitions, Notices, Correspondence
        """
        super().select_event_category(page, category)

    def set_page_count(self, page: Page, count: int) -> None:
        """Set the document page count (REQUIRED for briefs)."""
        for selector in [
            "input[name='pageCount']",
            "input[name='page_count']",
            "input[name*='page'][type='text']",
        ]:
            el = page.query_selector(selector)
            if el:
                el.fill(str(count))
                logger.info("Set page count: %d", count)
                return
        logger.warning("Page count field not found — may cause rejection for briefs")

    def set_word_count(self, page: Page, count: int) -> None:
        """Set the document word count (REQUIRED for briefs)."""
        for selector in [
            "input[name='wordCount']",
            "input[name='word_count']",
            "input[name*='word'][type='text']",
        ]:
            el = page.query_selector(selector)
            if el:
                el.fill(str(count))
                logger.info("Set word count: %d", count)
                return
        logger.warning("Word count field not found — may cause rejection for briefs")

    def select_filing_type(self, page: Page, filing_type: str) -> None:
        """Select appellate filing type (opening brief, reply brief, etc.)."""
        for selector in [
            "select[name='filingType']",
            "#filing_type",
            "select[name*='type']",
        ]:
            el = page.query_selector(selector)
            if el:
                page.select_option(selector, label=filing_type)
                page.wait_for_load_state("networkidle")
                logger.info("Selected filing type: %s", filing_type)
                return

    def check_certificate_of_compliance(self, page: Page, word_count: int = 0) -> None:
        """Check the certificate of compliance checkbox and fill word count.

        Appellate rules require certifying that the brief complies with
        length limits (typically 13,000 words for opening/response briefs).
        """
        cert_checkbox = page.query_selector(
            "input[name='certCompliance'], input[name='cert_compliance'], "
            "input[type='checkbox'][name*='cert']"
        )
        if cert_checkbox:
            cert_checkbox.check()
            logger.info("Checked certificate of compliance")

        # Fill word count in compliance section if present
        if word_count:
            self.set_word_count(page, word_count)
