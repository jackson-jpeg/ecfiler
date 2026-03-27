"""CM/ECF page navigation helpers.

Provides reusable navigation patterns for CM/ECF web pages across
different court types and configurations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


class NavigationError(Exception):
    """Raised when CM/ECF navigation fails."""


def wait_for_ecf_page(page: Page, timeout: int = 15000) -> None:
    """Wait for a CM/ECF page to fully load."""
    page.wait_for_load_state("networkidle", timeout=timeout)


def detect_error(page: Page) -> str | None:
    """Check if the current page shows a CM/ECF error.

    Returns the error text if found, None otherwise.
    """
    # Common CM/ECF error indicators
    error_selectors = [
        ".error",
        "#error",
        ".errorMessage",
        "font[color='red']",
        ".alert-danger",
    ]

    for selector in error_selectors:
        elements = page.query_selector_all(selector)
        for el in elements:
            text = el.inner_text().strip()
            if text and len(text) > 5:
                return text

    # Check for error in page title
    title = page.title()
    if "error" in title.lower():
        return f"Page title indicates error: {title}"

    return None


def navigate_to_filing(page: Page, ecf_url: str) -> None:
    """Navigate to the CM/ECF filing menu.

    Args:
        page: Playwright page
        ecf_url: Base ECF URL for the court
    """
    # NextGen CM/ECF filing URL pattern
    page.goto(f"{ecf_url}/cgi-bin/iquery.pl")
    wait_for_ecf_page(page)

    error = detect_error(page)
    if error:
        raise NavigationError(f"Error navigating to filing page: {error}")


def select_case(page: Page, case_number: str) -> dict[str, str]:
    """Enter a case number and retrieve case info.

    Args:
        page: Playwright page on the filing screen
        case_number: Case number (e.g., "1:24-cv-01234")

    Returns:
        Dict with case info: {"title": "...", "judge": "...", "status": "..."}
    """
    # Look for case number input field (varies by court)
    case_input = page.query_selector(
        "input[name='case_num'], input[name='caseNumber'], #case_num"
    )
    if not case_input:
        raise NavigationError("Cannot find case number input field")

    case_input.fill(case_number)
    page.keyboard.press("Tab")
    wait_for_ecf_page(page)

    error = detect_error(page)
    if error:
        raise NavigationError(f"Case lookup failed: {error}")

    # Try to extract case info from the page
    case_info: dict[str, str] = {"number": case_number}

    # Look for case title
    title_el = page.query_selector(".case_title, .caseTitle, #caseTitle")
    if title_el:
        case_info["title"] = title_el.inner_text().strip()

    return case_info


def get_dropdown_options(page: Page, selector: str) -> list[dict[str, str]]:
    """Extract all options from a select/dropdown element.

    Args:
        page: Playwright page
        selector: CSS selector for the <select> element

    Returns:
        List of {"value": "...", "text": "..."} dicts
    """
    options = page.evaluate(
        f"""
        () => {{
            const select = document.querySelector('{selector}');
            if (!select) return [];
            return Array.from(select.options).map(o => ({{
                value: o.value,
                text: o.textContent.trim()
            }}));
        }}
    """
    )
    return options or []


def upload_document(page: Page, file_path: str, selector: str = "input[type='file']") -> None:
    """Upload a PDF document via file input.

    Args:
        page: Playwright page
        file_path: Path to the PDF file
        selector: CSS selector for the file input
    """
    file_input = page.query_selector(selector)
    if not file_input:
        raise NavigationError(f"Cannot find file upload input: {selector}")

    file_input.set_input_files(file_path)
    wait_for_ecf_page(page)
