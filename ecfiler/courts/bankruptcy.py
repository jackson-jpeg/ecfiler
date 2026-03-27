"""Bankruptcy court-specific CM/ECF workflow overrides."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ecfiler.courts.base import BaseCourt

if TYPE_CHECKING:
    from playwright.sync_api import Page


class BankruptcyCourt(BaseCourt):
    """US Bankruptcy Court CM/ECF workflow.

    Bankruptcy courts have additional features:
    - XML Case Opening module for automated petition filing
    - Creditor matrix management
    - Means test forms
    - Schedules and statements
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
        """Upload a creditor matrix file (bankruptcy-specific).

        The creditor matrix is a text file listing all creditors
        for a bankruptcy case.
        """
        matrix_input = page.query_selector(
            "input[name='creditor_file'], input[type='file'][accept='.txt']"
        )
        if matrix_input:
            matrix_input.set_input_files(matrix_path)
            page.wait_for_load_state("networkidle")

    def select_chapter(self, page: Page, chapter: str) -> None:
        """Select bankruptcy chapter (7, 11, 12, 13, etc.)."""
        chapter_select = page.query_selector(
            "select[name='chapter'], #chapter_select"
        )
        if chapter_select:
            page.select_option(
                "select[name='chapter'], #chapter_select",
                label=f"Chapter {chapter}",
            )
            page.wait_for_load_state("networkidle")

    def fill_means_test(self, page: Page, data: dict[str, str]) -> None:
        """Fill means test form fields (Chapter 7 specific)."""
        for field_name, value in data.items():
            field_input = page.query_selector(f"input[name='{field_name}']")
            if field_input:
                field_input.fill(value)

    @property
    def supports_xml_filing(self) -> bool:
        """Whether this court supports XML case opening."""
        return "xml_case_opening" in self.profile.quirks
