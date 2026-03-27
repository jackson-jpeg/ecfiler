"""Base court profile defining the standard CM/ECF filing workflow.

Each court type (district, bankruptcy, appellate) extends this base
with its specific workflow steps and selector overrides.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from playwright.sync_api import Page


@dataclass
class CourtSelectors:
    """CSS selectors for CM/ECF form elements.

    Override per-court when the standard selectors don't match.
    """

    case_number_input: str = "input[name='case_num']"
    event_category_dropdown: str = "#category"
    event_list: str = "#event_list"
    file_upload: str = "input[type='file']"
    related_entry: str = "#related_doc"
    final_submit: str = "input[type='submit'][value='Submit']"
    confirm_submit: str = "input[type='submit']"
    party_checkboxes: str = "input[type='checkbox'][name='party']"
    docket_text: str = "textarea[name='docket_text']"


@dataclass
class CourtProfile:
    """Configuration for a single court."""

    court_id: str
    name: str
    court_type: str  # district, bankruptcy, appellate
    ecf_url: str
    selectors: CourtSelectors = field(default_factory=CourtSelectors)
    quirks: list[str] = field(default_factory=list)
    event_codes: list[dict[str, str]] = field(default_factory=list)

    @property
    def login_url(self) -> str:
        return f"{self.ecf_url}/cgi-bin/login.pl"

    @property
    def filing_url(self) -> str:
        return f"{self.ecf_url}/cgi-bin/iquery.pl"

    @property
    def domain(self) -> str:
        """Extract domain from ECF URL."""
        from urllib.parse import urlparse

        return urlparse(self.ecf_url).hostname or ""


class BaseCourt:
    """Standard NextGen CM/ECF workflow.

    This handles the most common filing flow. Court-specific subclasses
    override individual steps as needed.
    """

    def __init__(self, profile: CourtProfile) -> None:
        self.profile = profile
        self.selectors = profile.selectors

    def navigate_to_filing(self, page: Page) -> None:
        """Navigate to the filing entry point."""
        page.goto(self.profile.filing_url)
        page.wait_for_load_state("networkidle")

    def enter_case_number(self, page: Page, case_number: str) -> None:
        """Enter the case number in the search/filing form."""
        page.fill(self.selectors.case_number_input, case_number)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")

    def select_event_category(self, page: Page, category: str) -> None:
        """Select the event category from the dropdown."""
        page.select_option(self.selectors.event_category_dropdown, label=category)
        page.wait_for_load_state("networkidle")

    def select_event(self, page: Page, event_code: str) -> None:
        """Select the specific event from the event list."""
        page.select_option(self.selectors.event_list, value=event_code)
        page.wait_for_load_state("networkidle")

    def upload_document(self, page: Page, file_path: str) -> None:
        """Upload the main document PDF."""
        page.set_input_files(self.selectors.file_upload, file_path)
        page.wait_for_load_state("networkidle")

    def upload_attachment(self, page: Page, file_path: str, description: str = "") -> None:
        """Upload an attachment document."""
        # Many courts have an "Add Attachment" button
        add_btn = page.query_selector(
            "input[value='Add Attachment'], button:has-text('Add Attachment')"
        )
        if add_btn:
            add_btn.click()
            page.wait_for_load_state("networkidle")

        # Find the next available file input
        file_inputs = page.query_selector_all("input[type='file']")
        if file_inputs:
            file_inputs[-1].set_input_files(file_path)
            page.wait_for_load_state("networkidle")

        # Fill description if field exists
        if description:
            desc_inputs = page.query_selector_all(
                "input[name*='description'], input[name*='desc']"
            )
            if desc_inputs:
                desc_inputs[-1].fill(description)

    def select_related_entry(self, page: Page, docket_number: str) -> None:
        """Select a related docket entry."""
        related = page.query_selector(self.selectors.related_entry)
        if related:
            related.fill(docket_number)
            page.wait_for_load_state("networkidle")

    def select_parties(self, page: Page, party_names: list[str]) -> None:
        """Select filing parties from checkboxes."""
        checkboxes = page.query_selector_all(self.selectors.party_checkboxes)
        for cb in checkboxes:
            label = cb.evaluate("el => el.parentElement?.textContent?.trim() || ''")
            if any(name.lower() in label.lower() for name in party_names):
                cb.check()

    def get_confirmation_text(self, page: Page) -> str:
        """Extract the confirmation/summary text before final submit."""
        return page.inner_text("body")

    def click_final_submit(self, page: Page) -> None:
        """Click the final submit button."""
        page.click(self.selectors.final_submit)
        page.wait_for_load_state("networkidle")

    def get_receipt_info(self, page: Page) -> dict[str, str]:
        """Extract filing receipt information from the confirmation page."""
        text = page.inner_text("body")
        return {
            "page_text": text,
            "url": page.url,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> BaseCourt:
        """Create a court instance from a JSON config dict."""
        selectors = CourtSelectors()
        if sel_data := data.get("selectors"):
            for key, value in sel_data.items():
                if hasattr(selectors, key):
                    setattr(selectors, key, value)

        profile = CourtProfile(
            court_id=data["court_id"],
            name=data["name"],
            court_type=data.get("court_type", "district"),
            ecf_url=data["ecf_url"],
            selectors=selectors,
            quirks=data.get("quirks", []),
            event_codes=data.get("event_codes", []),
        )
        return cls(profile)
