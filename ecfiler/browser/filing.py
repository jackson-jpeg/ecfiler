"""Core filing form automation for CM/ECF.

This module provides high-level filing operations that combine
browser navigation with court-specific workflow logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecfiler.browser.session import BrowserSession
    from ecfiler.courts.base import BaseCourt
    from ecfiler.filing.models import Filing


@dataclass
class FilingStep:
    """A single step in the filing automation."""

    name: str
    description: str
    completed: bool = False
    screenshot_path: str = ""
    error: str = ""


@dataclass
class FilingAutomation:
    """Tracks and executes automated filing steps."""

    court: BaseCourt
    browser: BrowserSession
    filing: Filing
    steps: list[FilingStep] = field(default_factory=list)

    def execute_all(self) -> bool:
        """Execute all filing steps.

        Returns True if all steps completed without error.
        Stops at the final confirmation — does NOT click submit.
        """
        step_methods = [
            ("Navigate to filing", self._navigate),
            ("Enter case number", self._enter_case),
            ("Select event type", self._select_event),
            ("Upload main document", self._upload_main),
            ("Upload attachments", self._upload_attachments),
            ("Select related entry", self._select_related),
            ("Reach confirmation page", self._reach_confirmation),
        ]

        for name, method in step_methods:
            step = FilingStep(name=name, description="")
            self.steps.append(step)

            try:
                method()
                step.completed = True
                step.screenshot_path = str(
                    self.browser.screenshot(name.lower().replace(" ", "_"))
                )
            except Exception as e:
                step.error = str(e)
                return False

        return True

    def submit(self) -> None:
        """Click the final submit button.

        This should only be called after attorney confirmation.
        """
        self.court.click_final_submit(self.browser.page)
        self.browser.screenshot("submitted")

    def _navigate(self) -> None:
        self.court.navigate_to_filing(self.browser.page)

    def _enter_case(self) -> None:
        self.court.enter_case_number(
            self.browser.page, self.filing.case.case_number
        )

    def _select_event(self) -> None:
        self.court.select_event(self.browser.page, self.filing.event.code)

    def _upload_main(self) -> None:
        main_doc = self.filing.main_document
        if main_doc:
            self.court.upload_document(self.browser.page, main_doc.file_path)

    def _upload_attachments(self) -> None:
        for att in self.filing.attachments:
            self.court.upload_attachment(
                self.browser.page, att.file_path, att.description
            )

    def _select_related(self) -> None:
        if self.filing.related_entry:
            self.court.select_related_entry(
                self.browser.page, self.filing.related_entry.docket_number
            )

    def _reach_confirmation(self) -> None:
        """Navigate through any intermediate pages to reach the confirmation."""
        page = self.browser.page

        # Many courts have a "Next" button before the final confirmation
        next_btn = page.query_selector(
            "input[value='Next'], button:has-text('Next'), input[value='Continue']"
        )
        if next_btn:
            next_btn.click()
            page.wait_for_load_state("networkidle")
