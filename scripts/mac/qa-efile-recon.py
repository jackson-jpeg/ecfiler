"""[MAC] Read-only recon of the QA realm's Non-Attorney E-File Registration.

Session 7 (2026-11-13). Answers docs/qa-efile-registration.md open unknown 1
(which QA courts and roles the registration form offers) without registering
anything. It reuses the persisted QA session in ~/.ecfiler/pacer-profile
(`ecfiler-mac session login --qa` keeps it live), opens Manage My Account →
Maintenance, follows the Non-Attorney E-File Registration link, and records
every <select>'s options plus a screenshot of each page.

It never fills a field, ticks a box, or clicks anything but navigation links
and the court-type selector. Submitting the registration is an identity
attestation by the account holder and stays with him.

Usage: [MAC] ~/ecfiler/.venv/bin/python ~/ecfiler/scripts/mac/qa-efile-recon.py
Output: ~/.ecfiler/qa-efile-recon/<timestamp>/ (report.json + PNGs)
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import TimeoutError as PWTimeout
from playwright.sync_api import sync_playwright

START = "https://qa-pacer.psc.uscourts.gov/pscof/manage/maint.jsf"
PROFILE = Path.home() / ".ecfiler" / "pacer-profile"
OUT = Path.home() / ".ecfiler" / "qa-efile-recon" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LINK = re.compile(r"non-?attorney.*e-?fil|e-?file registration", re.I)


def selects(page) -> list[dict]:
    return page.evaluate(
        """() => Array.from(document.querySelectorAll('select')).map(s => ({
            id: s.id, name: s.name,
            label: (s.labels && s.labels[0] && s.labels[0].innerText) || '',
            options: Array.from(s.options).map(o => o.text.trim()).filter(Boolean)
        }))"""
    )


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    report: dict = {"started": datetime.now(timezone.utc).isoformat(), "pages": []}
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(START, wait_until="networkidle", timeout=60_000)

        def snap(tag: str) -> None:
            page.screenshot(path=str(OUT / f"{len(report['pages']):02d}-{tag}.png"), full_page=True)
            report["pages"].append({"tag": tag, "url": page.url, "title": page.title(), "selects": selects(page),
                                    "links": [t.strip() for t in page.locator("a").all_inner_texts() if t.strip()][:120]})

        snap("landing")
        if "login" in page.url.lower():
            report["result"] = "not-signed-in: run `ecfiler-mac session login --qa` first"
            ctx.close()
            (OUT / "report.json").write_text(json.dumps(report, indent=2))
            print(json.dumps({"result": report["result"], "out": str(OUT)}))
            return 2

        maint = page.get_by_text(re.compile(r"^\s*Maintenance\s*$", re.I))
        if maint.count():
            maint.first.click()
            page.wait_for_load_state("networkidle")
            snap("maintenance")

        link = page.get_by_text(LINK)
        if not link.count():
            report["result"] = "no e-file registration link found on Maintenance"
        else:
            link.first.click()
            page.wait_for_load_state("networkidle")
            snap("efile-registration")
            # Court type is a navigation choice that repopulates the court
            # list; read the court list once per type. Nothing else is touched.
            for s in selects(page):
                if re.search(r"court\s*type", s["label"] + s["id"] + s["name"], re.I):
                    sel = page.locator(f"select#{s['id']}" if s["id"] else f"select[name='{s['name']}']")
                    for opt in s["options"]:
                        if re.search(r"select|choose", opt, re.I):
                            continue
                        try:
                            sel.select_option(label=opt)
                            page.wait_for_load_state("networkidle", timeout=15_000)
                        except PWTimeout:
                            pass
                        snap(f"court-type-{re.sub(r'[^a-z]+', '-', opt.lower())[:30]}")
                    break
            report["result"] = "read"
        ctx.close()
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({"result": report["result"], "out": str(OUT), "pages": len(report["pages"])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
