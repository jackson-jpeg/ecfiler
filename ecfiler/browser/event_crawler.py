"""Event-catalog crawler.

Logs into a court's CM/ECF training database and enumerates every filing
event in every category. The training DB is explicitly intended for
practice filings and is accessible to any PACER account holder, so
enumerating its event picker is the legitimate source for per-court
event-code catalogs.

Output schema is a superset of ecfiler/courts/data/event_codes/*.json so
crawled catalogs can drop in alongside the curated ones.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from ecfiler.browser.session import BrowserSession
from ecfiler.courts.base import CourtProfile
from ecfiler.logging import get_logger

if TYPE_CHECKING:
    from playwright.sync_api import Page

logger = get_logger(__name__)


# CM/ECF top-level menus to visit. Each menu exposes a different event
# category tree. The URLs are stable across courts for legacy CM/ECF;
# NextGen uses the same cgi paths but sometimes behind a menu frame.
DISTRICT_MENUS: dict[str, str] = {
    "civil": "/cgi-bin/DisplayMenu.pl?Civil",
    "criminal": "/cgi-bin/DisplayMenu.pl?Criminal",
}
BANKRUPTCY_MENUS: dict[str, str] = {
    "bankruptcy": "/cgi-bin/DisplayMenu.pl?Bankruptcy",
    "adversary": "/cgi-bin/DisplayMenu.pl?Adversary",
}
APPELLATE_MENUS: dict[str, str] = {
    "filing": "/cgi-bin/DisplayMenu.pl?Filing",
}


@dataclass
class CrawledEvent:
    code: str
    description: str
    category: str
    subcategory: str = ""


@dataclass
class CrawlResult:
    court_id: str
    court_type: str
    source_url: str
    events: list[CrawledEvent] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_json_schema(self) -> dict:
        """Group into the {categories: {name: [events]}} schema used by events.py.

        Dedupes (code, description) within each category — CM/ECF menus
        sometimes surface the same event picker under multiple paths.
        """
        grouped: dict[str, list[dict]] = {}
        for e in self.events:
            key = e.category if not e.subcategory else f"{e.category} / {e.subcategory}"
            existing = grouped.setdefault(key, [])
            if not any(x["code"] == e.code and x["description"] == e.description for x in existing):
                existing.append({"code": e.code, "description": e.description})
        return {
            "description": f"Crawled event codes for {self.court_id}",
            "court_type": self.court_type,
            "source_url": self.source_url,
            "categories": grouped,
        }


class EventCrawler:
    """Walks a court's training DB and extracts its full event catalog."""

    # Conservative — training DBs are for practice but shared infra.
    REQUEST_DELAY_SECONDS = 1.0

    def __init__(
        self,
        profile: CourtProfile,
        session: BrowserSession,
        *,
        delay: float | None = None,
    ) -> None:
        self.profile = profile
        self.session = session
        self.delay = self.REQUEST_DELAY_SECONDS if delay is None else delay

    def login(self, username: str, password: str) -> bool:
        """Log into the training DB. Uses the same PACER CSO form as prod."""
        ok = self.session.login_via_form(self.profile.training_login_url, username, password)
        if not ok:
            logger.warning("Training DB login failed for %s", self.profile.court_id)
        return ok

    def crawl(self) -> CrawlResult:
        result = CrawlResult(
            court_id=self.profile.court_id,
            court_type=self.profile.court_type,
            source_url=self.profile.training_login_url.rsplit("/", 2)[0],
        )

        menus = self._menus_for_court_type()
        page = self.session.page
        training_base = result.source_url

        for category, menu_path in menus.items():
            logger.info("Crawling menu: %s (%s)", category, menu_path)
            try:
                page.goto(f"{training_base}{menu_path}")
                page.wait_for_load_state("networkidle")
            except Exception as e:
                result.warnings.append(f"{category}: could not load menu — {e}")
                continue

            links = self._collect_event_links(page)
            for href, label in links:
                time.sleep(self.delay)
                try:
                    events = self._enumerate_events_on_page(page, training_base, href)
                    for code, desc in events:
                        result.events.append(
                            CrawledEvent(
                                code=code,
                                description=desc,
                                category=category,
                                subcategory=label,
                            )
                        )
                except Exception as e:
                    result.warnings.append(f"{category}/{label}: {e}")

        return result

    def _menus_for_court_type(self) -> dict[str, str]:
        if self.profile.court_type == "district":
            return DISTRICT_MENUS
        if self.profile.court_type == "bankruptcy":
            return BANKRUPTCY_MENUS
        if self.profile.court_type == "appellate":
            return APPELLATE_MENUS
        return {}

    # Top-nav / cross-cutting links that aren't filing categories.
    NON_FILING_LINK_WORDS = {
        "query", "reports", "utilities", "search", "help", "logout",
        "login", "home", "account", "manage", "maintain", "notice",
        "docket report", "history", "written opinions", "civil cases",
        "criminal cases", "judge", "hearing", "calendar",
    }

    def _collect_event_links(self, page: Page) -> list[tuple[str, str]]:
        """From a CM/ECF category menu, collect (href, label) for each filing sub-category.

        CM/ECF menus render filing groups as <a> tags pointing to cgi scripts
        that show checkbox or select lists of events. Top-nav links (Query,
        Reports, Utilities, etc.) point to non-filing pages and must be excluded.
        """
        anchors = page.query_selector_all("a[href*='cgi-bin/']")
        pairs: list[tuple[str, str]] = []
        seen_hrefs: set[str] = set()
        for a in anchors:
            href = a.get_attribute("href") or ""
            text = (a.inner_text() or "").strip()
            if not href or not text:
                continue
            if "DisplayMenu" in href:
                continue
            if href in seen_hrefs:
                continue
            low = text.lower()
            if any(w in low for w in self.NON_FILING_LINK_WORDS):
                continue
            seen_hrefs.add(href)
            pairs.append((href, text))
        return pairs

    def _enumerate_events_on_page(
        self, page: Page, base: str, href: str
    ) -> list[tuple[str, str]]:
        """Visit an event-picker page and extract every (code, description) pair.

        Handles both common widgets:
        - <select> with <option value="code">description</option>
        - checkbox list <input type=checkbox name=event value=code> + label text
        """
        url = href if href.startswith("http") else f"{base}{href}" if href.startswith("/") else f"{base}/cgi-bin/{href.lstrip('/')}"
        page.goto(url)
        page.wait_for_load_state("networkidle")

        pairs: list[tuple[str, str]] = []

        # Select-option style — only accept selects whose name/id look like an
        # event picker. CM/ECF Nature-of-Suit and case-type pickers also use
        # <select>, so unfiltered scraping produces hundreds of false positives.
        event_selects = page.query_selector_all(
            "select[name*='event' i], select[id*='event' i], "
            "select[name='deferred'], select[name='selected_event']"
        )
        for sel in event_selects:
            for opt in sel.query_selector_all("option"):
                val = (opt.get_attribute("value") or "").strip()
                txt = (opt.inner_text() or "").strip()
                if val and txt and val.lower() not in {"", "none", "select one", "-"}:
                    pairs.append((val, txt))

        # Checkbox style (covers event-picker pages that use multi-select)
        checkboxes = page.query_selector_all("input[type='checkbox']")
        for cb in checkboxes:
            val = (cb.get_attribute("value") or "").strip()
            name = (cb.get_attribute("name") or "").lower()
            if not val or "event" not in name:
                continue
            label_text = ""
            cb_id = cb.get_attribute("id")
            if cb_id:
                lbl = page.query_selector(f"label[for='{cb_id}']")
                if lbl:
                    label_text = (lbl.inner_text() or "").strip()
            if not label_text:
                label_text = val
            pairs.append((val, label_text))

        return pairs


def save_catalog(result: CrawlResult, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{result.court_id}.json"
    path.write_text(json.dumps(result.to_json_schema(), indent=2))
    return path
