"""Playwright browser session management for CM/ECF interaction."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from ecfiler.config import CONFIG_DIR

if TYPE_CHECKING:
    from playwright.sync_api import Playwright

SCREENSHOTS_DIR = CONFIG_DIR / "screenshots"
TRACES_DIR = CONFIG_DIR / "traces"


class BrowserSession:
    """Manages a Playwright browser session for CM/ECF filing.

    Handles browser lifecycle, cookie management, and session state.
    """

    def __init__(self, headless: bool = True, slow_mo: int = 100) -> None:
        self.headless = headless
        self.slow_mo = slow_mo
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._screenshot_count = 0

        SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        TRACES_DIR.mkdir(parents=True, exist_ok=True)

    def start(self) -> Page:
        """Launch browser and create a new page."""
        self._pw = sync_playwright().start()
        self._browser = self._pw.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
        )
        self._context = self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        # Start tracing for debug/audit
        self._context.tracing.start(screenshots=True, snapshots=True)
        self._page = self._context.new_page()
        return self._page

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser session not started. Call start() first.")
        return self._page

    def inject_pacer_token(self, token: str, court_domain: str) -> None:
        """Inject PACER authentication token as a cookie.

        This allows the browser session to use a programmatically obtained
        PACER token instead of going through the login form.
        """
        if self._context is None:
            raise RuntimeError("Browser session not started.")

        self._context.add_cookies([
            {
                "name": "NextGenCSO",
                "value": token,
                "domain": court_domain,
                "path": "/",
                "httpOnly": True,
                "secure": True,
            },
            {
                "name": "NextGenCSO",
                "value": token,
                "domain": ".uscourts.gov",
                "path": "/",
                "httpOnly": True,
                "secure": True,
            },
        ])

    def login_via_form(self, login_url: str, username: str, password: str) -> bool:
        """Fall back to form-based PACER login if token injection fails.

        Returns True if login succeeded (detected by navigation to CM/ECF main page).
        """
        page = self.page
        page.goto(login_url)
        page.wait_for_load_state("networkidle")

        # NextGen CM/ECF login form
        page.fill("input[name='loginId'], input[name='login'], #loginId", username)
        page.fill("input[name='password'], input[type='password']", password)
        page.click("input[type='submit'], button[type='submit']")
        page.wait_for_load_state("networkidle")

        # Check if we landed on the main menu (successful login)
        return "MainMenu" in page.url or "cgi-bin" in page.url

    def screenshot(self, label: str = "") -> Path:
        """Capture a screenshot of the current page.

        Args:
            label: Descriptive label for the screenshot filename

        Returns:
            Path to the saved screenshot
        """
        self._screenshot_count += 1
        name = f"{self._screenshot_count:03d}"
        if label:
            name += f"_{label}"
        path = SCREENSHOTS_DIR / f"{name}.png"
        self.page.screenshot(path=str(path), full_page=True)
        return path

    def get_page_text(self) -> str:
        """Extract visible text from the current page."""
        return self.page.inner_text("body")

    def get_page_html(self) -> str:
        """Get the current page's HTML content."""
        return self.page.content()

    def save_receipt(self, case_id: str, docket_number: str) -> Path:
        """Save the current page (filing receipt) as HTML.

        Args:
            case_id: Case identifier for the filename
            docket_number: Docket entry number

        Returns:
            Path to the saved receipt
        """
        from datetime import datetime

        from ecfiler.config import RECEIPTS_DIR

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{case_id}_{docket_number}.html"
        path = RECEIPTS_DIR / filename
        path.write_text(self.get_page_html())
        return path

    def stop(self) -> None:
        """Save trace and close browser."""
        if self._context:
            try:
                trace_path = TRACES_DIR / "latest_trace.zip"
                self._context.tracing.stop(path=str(trace_path))
            except Exception:
                pass
            self._context.close()

        if self._browser:
            self._browser.close()

        if self._pw:
            self._pw.stop()

        self._page = None
        self._context = None
        self._browser = None
        self._pw = None

    def __enter__(self) -> BrowserSession:
        self.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.stop()
