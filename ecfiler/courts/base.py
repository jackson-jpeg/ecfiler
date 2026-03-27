"""Base court profile defining the standard CM/ECF filing workflow.

Each court type (district, bankruptcy, appellate) extends this base
with its specific workflow steps and selector overrides.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from ecfiler.logging import get_logger

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = get_logger(__name__)


class ECFFormError(Exception):
    """Raised when a CM/ECF form interaction fails."""


@dataclass
class CourtSelectors:
    """CSS selectors for CM/ECF form elements.

    Based on real NextGen CM/ECF HTML structure (SDNY, MN District).
    The CM/ECF filing flow is multi-page — each step loads a new page
    via cgi-bin scripts. The workflow from the MN District manual:

    1. Menu: Civil > Motions and Related Filings > Motions
    2. ECF Filing Tips page → click Next
    3. Case number entry → click Next
    4. Case confirmation → click Next
    5. Event type selection (checkboxes, not dropdown) → click Next
    6. Party selection (checkboxes) → click Next
    7. Browse for main document + attachments → click Next
    8. Docket text modification → click Next
    9. Final confirmation → click Next to submit
    10. NEF confirmation page

    Login uses PACER Central Sign-On (CSO) at pacer.login.uscourts.gov:
    - loginForm:loginName (username)
    - loginForm:password (password)
    - loginForm:clientCode (application ID)

    Override per-court when the standard selectors don't match.
    """

    # Case number entry (step 3)
    case_number_input: str = "input[name='case_num']"
    # Event type — CM/ECF uses checkboxes on some courts, dropdowns on others
    event_category_dropdown: str = "#category"
    event_list: str = "#event_list"
    event_checkboxes: str = "input[type='checkbox'][name*='event'], input[type='radio'][name*='event']"
    # Document upload (step 7)
    file_upload: str = "input[type='file']"
    file_browse_button: str = "input[value='Browse...'], button:has-text('Browse')"
    # Related document (step for answers/responses)
    related_entry: str = "input[type='checkbox'][name*='doc'], input[type='radio'][name*='doc']"
    # Navigation between form pages
    next_button: str = "input[value='Next'], button:has-text('Next')"
    back_button: str = "input[value='Back'], button:has-text('Back')"
    # Final submission (step 9 → 10)
    final_submit: str = "input[value='Next']"  # The final "Next" IS the submit
    confirm_submit: str = "input[type='submit']"
    # Party selection (step 6 — checkboxes with party names)
    party_checkboxes: str = "input[type='checkbox']"
    # Docket text (step 8)
    docket_text: str = "textarea, input[type='text'][name*='docket'], input[type='text'][name*='text']"
    brief_notice: str = "input[name='short_title'], input[type='text']"
    fee_status: str = "select[name='fee_status']"
    # Attorney-party association (first filing in a case)
    attorney_association: str = "input[type='checkbox'][name*='attorney'], input[type='checkbox'][name*='assoc']"
    lead_attorney: str = "input[type='checkbox'][name*='lead']"
    notice_checkbox: str = "input[type='checkbox'][name*='notice']"


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
        """Navigate to the CM/ECF filing menu.

        Real CM/ECF has a menu bar: Civil | Criminal | Query | Reports | Utilities
        Under Civil: Initial Pleadings and Service, Motions and Related Filings, etc.
        We navigate to the base ECF page which shows this menu.
        """
        page.goto(self.profile.ecf_url)
        page.wait_for_load_state("networkidle")

    def click_menu(self, page: Page, menu_path: str) -> None:
        """Navigate the CM/ECF menu bar.

        Args:
            menu_path: Menu path like "Civil > Motions and Related Filings > Motions"
        """
        parts = [p.strip() for p in menu_path.split(">")]
        for part in parts:
            link = page.query_selector(f"a:has-text('{part}'), td:has-text('{part}') a")
            if link:
                link.click()
                page.wait_for_load_state("networkidle")
                logger.debug("Clicked menu: %s", part)
            else:
                logger.warning("Menu item not found: %s", part)

    def click_next(self, page: Page) -> None:
        """Click the Next button to advance to the next form page."""
        for selector in [
            self.selectors.next_button,
            "input[value='Next']",
            "button:has-text('Next')",
        ]:
            el = page.query_selector(selector)
            if el:
                el.click()
                page.wait_for_load_state("networkidle")
                return
        raise ECFFormError("Next button not found")

    def enter_case_number(self, page: Page, case_number: str) -> None:
        """Enter the case number in the search/filing form."""
        selector = self.selectors.case_number_input
        el = page.query_selector(selector)
        if not el:
            raise ECFFormError(f"Case number input not found: {selector}")

        page.fill(selector, case_number)
        page.keyboard.press("Enter")
        page.wait_for_load_state("networkidle")
        logger.info("Entered case number: %s", case_number)

        # Check for error after case entry
        error = self._detect_page_error(page)
        if error:
            raise ECFFormError(f"Case lookup failed: {error}")

    def select_event_category(self, page: Page, category: str) -> None:
        """Select the event category from the dropdown."""
        selector = self.selectors.event_category_dropdown
        el = page.query_selector(selector)
        if not el:
            logger.debug("Event category dropdown not found (%s) — court may not use categories", selector)
            return  # Some courts skip the category step

        page.select_option(selector, label=category)
        page.wait_for_load_state("networkidle")

    def select_event(self, page: Page, event_code: str) -> None:
        """Select the specific event from the event list."""
        selector = self.selectors.event_list
        el = page.query_selector(selector)
        if not el:
            raise ECFFormError(f"Event list not found: {selector}")

        page.select_option(selector, value=event_code)
        page.wait_for_load_state("networkidle")
        logger.info("Selected event code: %s", event_code)

    def upload_document(self, page: Page, file_path: str) -> None:
        """Upload the main document PDF."""
        selector = self.selectors.file_upload
        el = page.query_selector(selector)
        if not el:
            raise ECFFormError(f"File upload input not found: {selector}")

        page.set_input_files(selector, file_path)
        page.wait_for_load_state("networkidle")
        logger.info("Uploaded document: %s", file_path)

        error = self._detect_page_error(page)
        if error:
            raise ECFFormError(f"Document upload failed: {error}")

    def upload_attachment(self, page: Page, file_path: str, description: str = "") -> None:
        """Upload an attachment document."""
        add_btn = page.query_selector(
            "input[value='Add Attachment'], button:has-text('Add Attachment'), "
            "a:has-text('Add Attachment')"
        )
        if add_btn:
            add_btn.click()
            page.wait_for_load_state("networkidle")

        file_inputs = page.query_selector_all("input[type='file']")
        if not file_inputs:
            raise ECFFormError("No file upload input found for attachment")

        # Use the last file input (new one created for attachment)
        file_inputs[-1].set_input_files(file_path)
        page.wait_for_load_state("networkidle")

        if description:
            # Look for description field near the last file input
            desc_input = page.query_selector(
                "input[name*='description']:last-of-type, "
                "input[name*='desc']:last-of-type, "
                "select[name*='type']:last-of-type"
            )
            if desc_input:
                tag = desc_input.evaluate("el => el.tagName")
                if tag == "SELECT":
                    page.select_option(desc_input, label=description)
                else:
                    desc_input.fill(description)

        logger.info("Uploaded attachment: %s (%s)", file_path, description)

    def fill_docket_text(self, page: Page, docket_text: str) -> None:
        """Fill the docket text field (required by most courts).

        This is the brief description that appears on the docket sheet.
        """
        selector = self.selectors.docket_text
        el = page.query_selector(selector)
        if el:
            page.fill(selector, docket_text)
            logger.info("Filled docket text: %s", docket_text[:50])
        else:
            logger.debug("Docket text field not found (%s)", selector)

    def fill_brief_notice(self, page: Page, notice_text: str) -> None:
        """Fill the brief notice / short title field (required for motions)."""
        selector = self.selectors.brief_notice
        el = page.query_selector(selector)
        if el:
            page.fill(selector, notice_text)
            logger.info("Filled brief notice: %s", notice_text[:50])
        else:
            logger.debug("Brief notice field not found (%s)", selector)

    def select_fee_status(self, page: Page, fee_status: str = "paid") -> None:
        """Select fee status (paid, waived, IFP).

        Args:
            fee_status: "paid", "waived", or "ifp"
        """
        selector = self.selectors.fee_status
        el = page.query_selector(selector)
        if el:
            page.select_option(selector, value=fee_status)
            logger.info("Selected fee status: %s", fee_status)

    def select_sealing_level(self, page: Page, level: str) -> None:
        """Select document sealing/restriction level.

        Args:
            level: "public", "sealed", "restricted", "ex_parte"
        """
        if level == "public":
            return  # Default, no action needed

        # Look for sealing-related controls
        for selector in [
            "select[name*='seal']",
            "select[name*='restrict']",
            "input[type='checkbox'][name*='seal']",
            "#sealDocument",
        ]:
            el = page.query_selector(selector)
            if el:
                tag = el.evaluate("el => el.tagName")
                if tag == "SELECT":
                    page.select_option(selector, label=level.replace("_", " ").title())
                elif tag == "INPUT":
                    el.check()
                logger.info("Set sealing level: %s", level)
                return

        logger.warning(
            "Sealing controls not found — document will be filed as public. "
            "For sealed filings, verify the court's sealing procedure."
        )

    def select_related_entry(self, page: Page, docket_number: str) -> None:
        """Select a related docket entry.

        Tries dropdown selection first, falls back to text input.
        """
        selector = self.selectors.related_entry
        el = page.query_selector(selector)
        if not el:
            logger.debug("Related entry field not found (%s)", selector)
            return

        tag = el.evaluate("el => el.tagName")
        if tag == "SELECT":
            # Try to find the option matching the docket number
            options = page.evaluate(
                "(sel) => Array.from(document.querySelector(sel)?.options || []).map(o => ({value: o.value, text: o.text}))",
                selector,
            )
            match = next(
                (o for o in (options or []) if docket_number in o.get("text", "")),
                None,
            )
            if match:
                page.select_option(selector, value=match["value"])
            else:
                logger.warning("Docket #%s not found in dropdown options", docket_number)
        else:
            el.fill(docket_number)

        page.wait_for_load_state("networkidle")
        logger.info("Selected related entry: Docket #%s", docket_number)

    def select_parties(self, page: Page, party_names: list[str]) -> int:
        """Select filing parties from checkboxes.

        Returns the number of parties successfully selected.
        """
        checkboxes = page.query_selector_all(self.selectors.party_checkboxes)
        if not checkboxes:
            logger.warning("No party checkboxes found (%s)", self.selectors.party_checkboxes)
            return 0

        selected = 0
        for cb in checkboxes:
            label = cb.evaluate("el => el.parentElement?.textContent?.trim() || ''")
            # Use word-boundary matching to avoid partial name matches
            for name in party_names:
                if name.lower() == label.lower() or f" {name.lower()} " in f" {label.lower()} ":
                    cb.check()
                    selected += 1
                    logger.info("Selected party: %s", label)
                    break

        if selected == 0:
            logger.warning(
                "No matching parties found for %s among %d checkboxes",
                party_names,
                len(checkboxes),
            )

        return selected

    def handle_attorney_association(self, page: Page, party_name: str) -> None:
        """Handle the attorney-party association screen.

        Per the MN District manual: on first filing in a case, CM/ECF shows
        a screen to associate the attorney with a party. This includes:
        - Checkbox to associate attorney to party
        - Optional "Lead" checkbox
        - "Notice" checkbox (strongly recommended — enables NEF emails)
        """
        # Check if association screen appeared
        assoc_checkboxes = page.query_selector_all(self.selectors.attorney_association)
        if not assoc_checkboxes:
            return  # Not the first filing — association already exists

        logger.info("Attorney association screen detected")

        # Check the box next to the party name
        for cb in assoc_checkboxes:
            label = cb.evaluate("el => el.parentElement?.textContent?.trim() || ''")
            if party_name.lower() in label.lower():
                cb.check()
                logger.info("Associated attorney with party: %s", label)
                break

        # Always check the Notice checkbox to receive NEFs
        notice_cb = page.query_selector(self.selectors.notice_checkbox)
        if notice_cb:
            notice_cb.check()
            logger.info("Enabled electronic notice")

        self.click_next(page)

    def get_confirmation_text(self, page: Page) -> str:
        """Extract the filing summary from the confirmation page.

        Tries to find the specific confirmation/summary section rather
        than returning the entire page.
        """
        # Try common confirmation containers
        for selector in [
            "#confirmationText",
            ".confirmation",
            "#summary",
            "table.confirmation",
            "#content table",
            "form table",
        ]:
            el = page.query_selector(selector)
            if el:
                text = el.inner_text().strip()
                if len(text) > 20:
                    return text

        # Fallback: get body text but try to clean it up
        body = page.inner_text("body")
        # Remove common navigation/menu noise
        lines = body.split("\n")
        meaningful = [
            line.strip()
            for line in lines
            if line.strip() and len(line.strip()) > 3 and not line.strip().startswith("©")
        ]
        return "\n".join(meaningful[:50])

    def click_final_submit(self, page: Page) -> None:
        """Click the final submit button."""
        # Try multiple submit button patterns
        for selector in [
            self.selectors.final_submit,
            "input[type='submit'][value*='Submit']",
            "input[type='submit'][value*='Accept']",
            "button[type='submit']",
            "input[type='submit']",
        ]:
            el = page.query_selector(selector)
            if el:
                el.click()
                page.wait_for_load_state("networkidle")
                logger.info("Clicked submit button: %s", selector)
                return

        raise ECFFormError("Submit button not found on confirmation page")

    def get_receipt_info(self, page: Page) -> dict[str, str]:
        """Extract filing receipt information from the confirmation page."""
        text = page.inner_text("body")
        url = page.url

        info: dict[str, str] = {
            "page_text": text,
            "url": url,
        }

        # Try to extract specific fields from the receipt
        # Docket number pattern: "Docket #58" or "docket entry #58"
        docket_match = re.search(r"[Dd]ocket\s*(?:#|entry\s*#?)\s*(\d+)", text)
        if docket_match:
            info["docket_number"] = docket_match.group(1)

        # Filing timestamp
        time_match = re.search(
            r"(?:filed|entered|received)\s*(?:on)?\s*(\d{1,2}/\d{1,2}/\d{2,4}\s+\d{1,2}:\d{2})",
            text,
            re.IGNORECASE,
        )
        if time_match:
            info["filed_at"] = time_match.group(1)

        # Case number confirmation
        case_match = re.search(r"(\d+:\d{2}-[a-z]{2}-\d{4,5})", text)
        if case_match:
            info["case_number"] = case_match.group(1)

        logger.info("Receipt extracted: %s", {k: v[:30] for k, v in info.items() if k != "page_text"})
        return info

    def _detect_page_error(self, page: Page) -> str | None:
        """Check if the current CM/ECF page shows an error."""
        for selector in [
            ".error",
            "#error",
            ".errorMessage",
            "font[color='red']",
            ".alert-danger",
            ".alert-error",
        ]:
            elements = page.query_selector_all(selector)
            for el in elements:
                text = el.inner_text().strip()
                if text and len(text) > 5:
                    logger.warning("CM/ECF error detected: %s", text[:100])
                    return text
        return None

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
