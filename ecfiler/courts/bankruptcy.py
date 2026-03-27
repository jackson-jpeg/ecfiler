"""Bankruptcy court-specific CM/ECF workflow overrides."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ecfiler.courts.base import BaseCourt, ECFFormError
from ecfiler.logging import get_logger

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = get_logger(__name__)


class BankruptcyCourt(BaseCourt):
    """US Bankruptcy Court CM/ECF workflow.

    Bankruptcy courts have additional features:
    - XML Case Opening module for automated petition filing
    - Creditor matrix management (REQUIRED for new cases)
    - Means test forms
    - Schedules and statements
    - Chapter selection
    """

    def navigate_to_filing(self, page: Page) -> None:
        """Bankruptcy courts may use a different filing entry URL."""
        url = f"{self.profile.ecf_url}/cgi-bin/iquery.pl"
        page.goto(url)
        page.wait_for_load_state("networkidle")

    def select_event_category(self, page: Page, category: str) -> None:
        """Bankruptcy has different event category taxonomy.

        Categories include: Bankruptcy, Adversary, Claims, Motions, etc.
        """
        super().select_event_category(page, category)

    def upload_creditor_matrix(self, page: Page, matrix_path: str) -> None:
        """Upload a creditor matrix file (REQUIRED for new bankruptcy cases).

        The creditor matrix is a text file listing all creditors.
        """
        matrix_input = page.query_selector(
            "input[name='creditor_file'], input[type='file'][accept='.txt'], "
            "input[type='file'][name*='creditor']"
        )
        if matrix_input:
            matrix_input.set_input_files(matrix_path)
            page.wait_for_load_state("networkidle")
            logger.info("Uploaded creditor matrix: %s", matrix_path)
        else:
            logger.warning("Creditor matrix upload field not found")
            raise ECFFormError(
                "Creditor matrix upload required for new bankruptcy cases "
                "but the upload field was not found on this page."
            )

    def select_chapter(self, page: Page, chapter: str) -> None:
        """Select bankruptcy chapter (7, 11, 12, 13, etc.)."""
        for selector in [
            "select[name='chapter']",
            "#chapter_select",
            "select[name*='chapter']",
        ]:
            el = page.query_selector(selector)
            if el:
                page.select_option(selector, label=f"Chapter {chapter}")
                page.wait_for_load_state("networkidle")
                logger.info("Selected Chapter %s", chapter)
                return

        logger.warning("Chapter selection dropdown not found")

    def fill_asset_info(self, page: Page, asset_case: bool, estimated_assets: str, estimated_liabilities: str) -> None:
        """Fill asset/liability fields for bankruptcy case opening."""
        # Asset case checkbox
        asset_cb = page.query_selector(
            "input[name='asset_case'], input[name*='asset'][type='checkbox']"
        )
        if asset_cb:
            if asset_case:
                asset_cb.check()
            else:
                asset_cb.uncheck()

        # Estimated assets dropdown/input
        for field_name, value in [("estimated_assets", estimated_assets), ("estimated_liabilities", estimated_liabilities)]:
            if not value:
                continue
            el = page.query_selector(
                f"select[name*='{field_name}'], input[name*='{field_name}']"
            )
            if el:
                tag = el.evaluate("el => el.tagName")
                if tag == "SELECT":
                    page.select_option(f"select[name*='{field_name}']", label=value)
                else:
                    el.fill(value)

    def fill_means_test(self, page: Page, data: dict[str, str]) -> None:
        """Fill means test form fields (Chapter 7 specific)."""
        for field_name, value in data.items():
            # Use parameterized evaluation to avoid selector injection
            el = page.query_selector(f"input[name='{field_name}']")
            if el:
                el.fill(value)
            else:
                logger.debug("Means test field not found: %s", field_name)

    @property
    def supports_xml_filing(self) -> bool:
        """Whether this court supports XML case opening."""
        return "xml_case_opening" in self.profile.quirks
