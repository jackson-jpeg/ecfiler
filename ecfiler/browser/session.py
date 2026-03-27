"""Playwright browser session management for CM/ECF interaction."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from ecfiler.config import CONFIG_DIR
from ecfiler.logging import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from playwright.sync_api import Playwright

SCREENSHOTS_DIR = CONFIG_DIR / "screenshots"
TRACES_DIR = CONFIG_DIR / "traces"


class BrowserSession:
    """Manages a Playwright browser session for CM/ECF filing.

    Handles browser lifecycle, cookie management, and session state.
    """

    DEFAULT_TIMEOUT = 30_000  # 30 seconds for page operations
    NAVIGATION_TIMEOUT = 60_000  # 60 seconds for page navigation

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
        logger.info("Starting browser session (headless=%s)", self.headless)
        self._pw = sync_playwright().start()
        # --no-sandbox needed in containers / root environments
        import os
        args = []
        if os.getuid() == 0 or os.environ.get("PLAYWRIGHT_NO_SANDBOX"):
            args.append("--no-sandbox")

        self._browser = self._pw.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            timeout=30_000,
            args=args,
        )
        self._context = self._browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        # Set default timeouts for all operations in this context
        self._context.set_default_timeout(self.DEFAULT_TIMEOUT)
        self._context.set_default_navigation_timeout(self.NAVIGATION_TIMEOUT)
        # Start tracing for debug/audit
        self._context.tracing.start(screenshots=True, snapshots=True)
        self._page = self._context.new_page()
        return self._page

    @property
    def page(self) -> Page:
        if self._page is None:
            raise RuntimeError("Browser session not started. Call start() first.")
        return self._page

    def login_with_token(self, token: str, ecf_url: str) -> bool:
        """Log into CM/ECF using a PACER API token.

        This bypasses the browser login form and MFA entirely by using
        the login.pl?csession= endpoint that CM/ECF uses internally
        after CSO authentication.

        Tested working against real SDNY CM/ECF (March 2026).

        Returns True if CM/ECF main menu loaded.
        """
        page = self.page
        page.goto(f"{ecf_url}/cgi-bin/login.pl?csession={token}")
        page.wait_for_load_state("networkidle")
        logger.info("Token login URL: %s", page.url[:80])

        body = page.inner_text("body")
        logged_in = any(w in body for w in ["Query", "Civil", "Reports", "Utilities", "Log Out"])
        if logged_in:
            logger.info("Token login succeeded — CM/ECF main menu loaded")
        else:
            logger.warning("Token login may have failed — checking page content")
        return logged_in

    def inject_pacer_token(self, token: str, court_domain: str) -> None:
        """Inject PACER authentication token as a cookie (legacy method).

        Prefer login_with_token() which uses the csession= URL approach
        and is confirmed working against real CM/ECF.
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
        """Log in via PACER Central Sign-On (CSO) form.

        NextGen CM/ECF redirects to pacer.login.uscourts.gov for auth.
        Real form field names (from live PACER CSO page):
        - loginForm:loginName (username/email)
        - loginForm:password (password)
        - loginForm:clientCode (optional, identifies application)
        - loginForm:fbtnLogin (submit button)

        Returns True if login succeeded.
        """
        page = self.page
        page.goto(login_url)
        page.wait_for_load_state("networkidle")
        logger.info("Navigated to login page: %s", page.url)

        # CM/ECF redirects to PACER CSO — wait for the login form
        # The real form is at pacer.login.uscourts.gov
        try:
            page.wait_for_selector(
                "#loginForm\\:loginName, input[name='loginForm:loginName']",
                timeout=15_000,
            )
        except Exception:
            # Fallback: try legacy selector patterns
            logger.debug("CSO login form not found, trying legacy selectors")

        # Try PACER CSO form fields (real NextGen)
        for username_sel in [
            "#loginForm\\:loginName",
            "input[name='loginForm:loginName']",
            "input[name='login']",
            "#loginId",
        ]:
            el = page.query_selector(username_sel)
            if el:
                el.fill(username)
                logger.debug("Filled username with selector: %s", username_sel)
                break

        for password_sel in [
            "#loginForm\\:password",
            "input[name='loginForm:password']",
            "input[type='password']",
        ]:
            el = page.query_selector(password_sel)
            if el:
                el.fill(password)
                logger.debug("Filled password with selector: %s", password_sel)
                break

        # Set client code to identify ECFiler
        client_code = page.query_selector(
            "#loginForm\\:clientCode, input[name='loginForm:clientCode']"
        )
        if client_code:
            client_code.fill("ecfiler")

        # Click login button
        for submit_sel in [
            "#loginForm\\:pbtnLogin",
            "button[name='loginForm:fbtnLogin']",
            "#loginForm input[type='submit']",
            "button[type='submit']",
            "input[type='submit']",
        ]:
            el = page.query_selector(submit_sel)
            if el:
                el.click()
                logger.debug("Clicked submit with selector: %s", submit_sel)
                break

        page.wait_for_load_state("networkidle")

        # After CSO login, PACER redirects back to CM/ECF
        # Check for the redaction agreement dialog (appears on first login)
        redaction_btn = page.query_selector(
            "#redactionConfirmation button, "
            "button:has-text('I Understand'), "
            "button:has-text('Accept')"
        )
        if redaction_btn:
            redaction_btn.click()
            page.wait_for_load_state("networkidle")
            logger.info("Accepted redaction agreement")

        # Verify we're on CM/ECF (not still on login page)
        url = page.url.lower()
        logged_in = (
            "cgi-bin" in url
            or "servlet" in url
            or "ecf." in url
            and "login" not in url
        )
        logger.info("Login %s (url: %s)", "succeeded" if logged_in else "failed", url[:80])
        return logged_in

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
