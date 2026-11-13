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
        assert "last updated: november 2026" in body
        assert "march 2026" not in body


@needs_server
def test_homepage_advertises_reachable_tools(anon_page) -> None:
    anon_page.goto(f"{WEB_URL}/", wait_until="networkidle")
    content = anon_page.content()
    for path in ("/tools", "/courts", "/events", "/fees", "/redaction"):
        assert f'href="{path}"' in content, f"no link to {path} on the homepage"


# --- Session 7 (2026-11-13): the site runs with no backend ------------------
#
# The API was retired from the VPS on 2026-09-24. Production builds with no
# BACKEND_URL; every surface that needs the API says so instead of failing,
# and the waitlist mails signups through Resend from a route handler.

WEB = REPO / "web"

# Screens touched in session 7. Standing rule: no em dashes in any text a
# user reads, and every screen we touch is cleaned and held to it here.
# (JSX comments are not user-facing and are stripped before checking.)
EM_DASH_CLEAN_SCREENS = [
    "app/page.tsx",
    "app/(app)/layout.tsx",
    "app/(tools)/tools/page.tsx",
    "app/(tools)/validate/page.tsx",
    "app/sign-up/[[...sign-up]]/page.tsx",
    "app/privacy/page.tsx",
    "app/terms/page.tsx",
    "app/error.tsx",
    "app/not-found.tsx",
    "components/workspace-offline.tsx",
    "lib/workspace.ts",
    "lib/validator.ts",
    "app/api/waitlist/route.ts",
]


def _strip_comments(src: str) -> str:
    src = re.sub(r"\{/\*.*?\*/\}", "", src, flags=re.S)  # JSX comments
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)  # block comments
    return re.sub(r"^\s*//.*$", "", src, flags=re.M)  # line comments


class TestNoBackendGuards:
    def test_no_unconditional_backend_proxy(self) -> None:
        cfg = (WEB / "next.config.ts").read_text(encoding="utf-8")
        assert '|| "https://api.ecfiler.com"' not in cfg, (
            "next.config.ts proxies /api/* to api.ecfiler.com by default; "
            "with no backend that is a 502 on every API path"
        )
        assert "if (!API) return [];" in cfg

    def test_waitlist_success_requires_ok_response(self) -> None:
        page = (WEB / "app" / "page.tsx").read_text(encoding="utf-8")
        assert "if (r.ok)" in page, (
            "the waitlist form must show success only on a 2xx; before "
            "session 7 a 502 was shown as 'You're on the list'"
        )
        assert "/api/waitlist/count" not in page

    def test_waitlist_route_answers_only_after_resend_accepts(self) -> None:
        route = (WEB / "app" / "api" / "waitlist" / "route.ts").read_text(encoding="utf-8")
        assert "https://api.resend.com/emails" in route
        assert "!resp || !resp.ok" in route
        assert "WAITLIST_NOTIFY_TO" in route
        # the inbox stays out of the public repo
        assert "sang3r" not in route.lower()

    def test_no_dead_ecfiler_mailboxes(self) -> None:
        # ecfiler.com has no MX record and no mailbox (session 7). The only
        # @ecfiler.com address allowed is the waitlist's sending identity.
        for f in list((WEB / "app").rglob("*.tsx")) + list((WEB / "components").rglob("*.tsx")):
            text = f.read_text(encoding="utf-8")
            assert not re.search(r"[\w.-]+@ecfiler\.com", text), (
                f"{f.relative_to(REPO)} shows an @ecfiler.com address, which cannot receive mail"
            )

    def test_validate_runs_in_the_browser(self) -> None:
        page = (WEB / "app" / "(tools)" / "validate" / "page.tsx").read_text(encoding="utf-8")
        assert "@/lib/validator" in page and "@/lib/api" not in page
        api = (WEB / "lib" / "api.ts").read_text(encoding="utf-8")
        assert "/api/validate" not in api.replace("POST /api/validate", "")

    def test_validator_mirrors_python_limits(self) -> None:
        import inspect

        from ecfiler.pdf import validator

        ts = (WEB / "lib" / "validator.ts").read_text(encoding="utf-8")
        default_mb = inspect.signature(validator.validate_pdf).parameters["max_size_mb"].default
        assert f"export const MAX_SIZE_MB = {default_mb};" in ts
        src = inspect.getsource(validator)
        assert "min(5, len(doc))" in src and "const TEXT_PAGES = 5;" in ts
        assert "len(page_text) > 20" in src and "const MIN_TEXT_CHARS = 20;" in ts
        assert '"pdfaid" in xmp.lower()' in src and 'includes("pdfaid")' in ts

    def test_no_em_dashes_on_session7_screens(self) -> None:
        for rel in EM_DASH_CLEAN_SCREENS:
            text = _strip_comments((WEB / rel).read_text(encoding="utf-8"))
            bad = [ln.strip()[:80] for ln in text.splitlines() if "—" in ln or "&mdash;" in ln]
            assert not bad, f"web/{rel} has user-facing em dashes: {bad}"


@needs_server
def test_api_health_answers_without_a_backend(anon_page) -> None:
    r = anon_page.request.get(f"{WEB_URL}/api/health")
    assert r.status == 200, f"/api/health answered {r.status}"
    body = r.json()
    assert body["service"] == "ecfiler-web" and body["workspace"] in ("offline", "online")


@needs_server
def test_unknown_api_path_is_404_not_502(anon_page) -> None:
    r = anon_page.request.get(f"{WEB_URL}/api/history")
    assert r.status < 500, f"/api/history answered {r.status}: a dead proxy is back"


@needs_server
def test_waitlist_rejects_a_bad_address(anon_page) -> None:
    r = anon_page.request.post(f"{WEB_URL}/api/waitlist", data={"email": "not-an-address"})
    assert r.status == 400


@needs_server
def test_waitlist_honeypot_sends_nothing_and_says_ok(anon_page) -> None:
    # The honeypot path returns before any mail is sent, so this is safe to
    # run against production.
    r = anon_page.request.post(
        f"{WEB_URL}/api/waitlist", data={"email": "bot@example.com", "website": "x"}
    )
    assert r.status == 200


@needs_server
def test_closed_workspace_says_so(anon_page) -> None:
    health = anon_page.request.get(f"{WEB_URL}/api/health").json()
    if health["workspace"] != "offline":
        pytest.skip("this build has a backend")
    for path in ("/file", "/sign-up"):
        anon_page.goto(f"{WEB_URL}{path}", wait_until="networkidle")
        assert "The filing workspace is not open yet" in anon_page.inner_text("body"), path
    anon_page.goto(f"{WEB_URL}/", wait_until="networkidle")
    assert 'href="/sign-up"' not in anon_page.content(), "homepage still sends visitors to sign up"


def _encrypted_pdf(src: Path, dst: Path) -> Path:
    import pikepdf

    with pikepdf.open(src) as pdf:
        pdf.save(dst, encryption=pikepdf.Encryption(user="secret", owner="secret"))
    return dst


@needs_server
def test_validate_tool_checks_pdfs_without_uploading(anon_page, tmp_path) -> None:
    sample = REPO / "docs" / "qa-roundtrip" / "sample-motion.pdf"
    uploads: list[str] = []
    anon_page.on("request", lambda req: uploads.append(req.url) if req.method == "POST" else None)

    anon_page.goto(f"{WEB_URL}/validate", wait_until="networkidle")
    anon_page.set_input_files("input[type=file]", str(sample))
    anon_page.wait_for_selector("text=1/1 passed", timeout=20_000)
    body = anon_page.inner_text("body")
    assert "Ready for CM/ECF filing" in body
    assert "PDF/A" in anon_page.inner_text("[data-testid=pdfa-check]")

    locked = _encrypted_pdf(sample, tmp_path / "locked.pdf")
    anon_page.set_input_files("input[type=file]", str(locked))
    anon_page.wait_for_selector("text=0/1 passed", timeout=20_000)
    assert "password-protected" in anon_page.inner_text("body")
    assert not [u for u in uploads if "/api/" in u], f"validate posted to the server: {uploads}"
