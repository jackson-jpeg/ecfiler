"""Every advertised free tool is reachable by an anonymous visitor.

Session 3 verified the site author-side and still shipped /courts behind the
sign-in redirect — the free tools lived inside the auth-gated (app) route
group. These tests verify as an outsider: a fresh browser context with no
session, no cookie, no auth header, against a real `next start` server.

The live tests need a running build. CI's web job (and
scripts/deploy/verify-web-anon.sh locally) builds the site, starts it, and
sets ECFILER_WEB_URL; without that the live tests skip and the static
layout guards below still run.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
WEB_URL = os.environ.get("ECFILER_WEB_URL", "")

# Tools advertised as free (pricing card, /tools index, footer). Each must
# render for an anonymous visitor without bouncing to /sign-in.
FREE_TOOL_PATHS = [
    "/tools",
    "/courts",
    "/events",
    "/fees",
    "/redaction",
    "/validate",
    "/certificate",
]


class TestStaticLayoutGuards:
    """Cheap always-on guards that don't need a server."""

    def test_free_tools_live_outside_the_auth_gate(self) -> None:
        app_group = REPO / "web" / "app" / "(app)"
        gated = sorted(p.name for p in app_group.iterdir() if p.is_dir())
        for tool in ("courts", "certificate", "validate", "events", "fees", "redaction", "tools"):
            assert tool not in gated, (
                f"web/app/(app)/{tool} is behind the sign-in redirect in "
                "(app)/layout.tsx — free tools belong in web/app/(tools)/"
            )

    def test_tools_group_has_no_auth_redirect(self) -> None:
        tools_group = REPO / "web" / "app" / "(tools)"
        assert tools_group.is_dir()
        for layout in tools_group.rglob("layout.tsx"):
            text = layout.read_text(encoding="utf-8")
            assert "redirect(" not in text and "auth()" not in text, (
                f"{layout.relative_to(REPO)} gates the free tools"
            )

    def test_every_advertised_tool_has_a_page(self) -> None:
        tools_group = REPO / "web" / "app" / "(tools)"
        pages = {p.parent.name for p in tools_group.rglob("page.tsx")}
        for path in FREE_TOOL_PATHS:
            assert path.lstrip("/") in pages, f"no page for advertised tool {path}"


needs_server = pytest.mark.skipif(
    not WEB_URL, reason="ECFILER_WEB_URL not set — no running web build"
)


@pytest.fixture(scope="module")
def anon_page():
    playwright = pytest.importorskip("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()  # no storage state: truly anonymous
        page = context.new_page()
        yield page
        browser.close()


@needs_server
def test_free_tools_reachable_anonymously(anon_page) -> None:
    for path in FREE_TOOL_PATHS:
        response = anon_page.goto(f"{WEB_URL}{path}", wait_until="networkidle")
        assert response is not None and response.ok, f"{path} did not load"
        assert "/sign-in" not in anon_page.url, (
            f"{path} bounced an anonymous visitor to {anon_page.url}"
        )


@needs_server
def test_court_search_works_without_an_account(anon_page) -> None:
    anon_page.goto(f"{WEB_URL}/courts", wait_until="networkidle")
    anon_page.fill("input", "florida")
    anon_page.wait_for_timeout(500)
    assert "Middle District of Florida" in anon_page.content()


@needs_server
def test_fee_lookup_answers_from_static_data(anon_page) -> None:
    anon_page.goto(f"{WEB_URL}/fees", wait_until="networkidle")
    anon_page.fill("input", "notice of appeal")
    anon_page.wait_for_timeout(300)
    assert "$605.00" in anon_page.content()


@needs_server
def test_redaction_scan_runs_in_the_browser(anon_page) -> None:
    anon_page.goto(f"{WEB_URL}/redaction", wait_until="networkidle")
    anon_page.fill("textarea", "Plaintiff SSN 123-45-6789 appears herein.")
    anon_page.click("text=Scan pasted text")
    anon_page.wait_for_timeout(300)
    assert "123-45-6789" in anon_page.content()
    assert "XXX-XX-6789" in anon_page.content()


@needs_server
def test_event_browser_lists_codes(anon_page) -> None:
    anon_page.goto(f"{WEB_URL}/events", wait_until="networkidle")
    assert "motion" in anon_page.content().lower()


@needs_server
def test_federal_courts_page_counts_are_consistent(anon_page) -> None:
    anon_page.goto(f"{WEB_URL}/federal-courts", wait_until="networkidle")
    text = anon_page.inner_text("body")
    m = re.search(r"(\d+) \+ (\d+) \+ (\d+) \+ (\d+) \+ (\d+) = (\d+)", text)
    assert m, "decomposition sentence missing from /federal-courts"
    parts = [int(x) for x in m.groups()]
    assert sum(parts[:5]) == parts[5], f"court decomposition does not sum: {parts}"


@needs_server
def test_legal_pages_carry_current_date(anon_page) -> None:
    for path in ("/privacy", "/terms"):
        anon_page.goto(f"{WEB_URL}{path}", wait_until="networkidle")
        body = anon_page.inner_text("body").lower()  # CSS uppercases the header
        assert "last updated: july 2026" in body
        assert "march 2026" not in body


@needs_server
def test_homepage_advertises_reachable_tools(anon_page) -> None:
    anon_page.goto(f"{WEB_URL}/", wait_until="networkidle")
    content = anon_page.content()
    for path in ("/tools", "/courts", "/events", "/fees", "/redaction"):
        assert f'href="{path}"' in content, f"no link to {path} on the homepage"
