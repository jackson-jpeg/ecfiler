"""Copy lint: the public surfaces may never re-acquire the claims we removed.

BRANDING.md's "Don't say" list, enforced. Each forbidden phrase either
describes server-side credential custody (the pattern the AO's July 2023
memorandum targets) or promises hosted automated submission (which does not
exist). If one of these reappears, either the architecture regressed or the
copy is lying — both are release blockers.
"""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

FORBIDDEN_PHRASES = [
    "aes-256",
    "automated cm/ecf filing",
    "automated cm/ecf submission",
    "credentials, encrypted",
    "encrypted server-side",
    "decrypted at the moment of filing",
    "live browser view",
    "automatically files your documents",
    "encrypted at rest with aes",
    # Session 4 purge (docs/claims-register.md, "Deleted rather than fixed"):
    # each of these was public copy with no implementing code behind it.
    "3-pass",
    "3 safety passes",
    "three safety passes",
    "stripe billing",
    "checkout via stripe",
    "hosted cm/ecf filing",
    "last updated: march 2026",
    "min saved per filing",
    "cancel anytime",
]

# Public-facing surfaces under lint. Python internals are covered by
# test_security.py's source scan instead.
SURFACES = [
    "web/app",
    "web/components",
    "web/lib",
    "README.md",
    "BRANDING.md",
]

ALLOWED_FILES = {
    # BRANDING.md quotes forbidden phrases inside its own "Don't say" list.
    "BRANDING.md",
}


def _files() -> list[Path]:
    out: list[Path] = []
    for surface in SURFACES:
        path = REPO / surface
        if path.is_file():
            out.append(path)
        elif path.is_dir():
            out.extend(
                p
                for p in path.rglob("*")
                if p.suffix in {".tsx", ".ts", ".md", ".html"} and p.is_file()
            )
    return out


def test_no_forbidden_copy() -> None:
    violations: list[str] = []
    for path in _files():
        if path.name in ALLOWED_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in FORBIDDEN_PHRASES:
            if phrase in text:
                violations.append(f"{path.relative_to(REPO)}: '{phrase}'")
    assert violations == [], "Forbidden public-copy claims found:\n" + "\n".join(
        violations
    )


def _outreach_files() -> list[Path]:
    """Correspondence drafts destined for courts, the AO, and state authorities."""
    out: list[Path] = []
    for surface in ("docs/outreach", "docs/fl/drafts"):
        d = REPO / surface
        if d.is_dir():
            out.extend(p for p in d.rglob("*.md") if p.is_file())
    return out


# The identity rules for outbound correspondence, settled in session 3:
#
# Jackson IS a litigation docketing specialist at a law firm in Tampa — the
# profession is real, and claiming it (in personal capacity) is allowed and
# often the right move. What outbound documents must never do:
#
#   1. Name, describe, or allude to the employer. A letter that reads as a
#      firm inquiry implicates an employer who has not consented, and the
#      recipient's answer files next to that name. Not "[FIRM NAME]", not
#      "a national law firm", not letterhead.
#   2. Use organizational voice. There is one person: no "we", "our", "us"
#      in any letter body — no "our filings", "our staff", "our computers".
#   3. Claim ECFiler is in use anywhere. It has never filed for a client;
#      no asserted user base, production operation, or filing practice.
#
# Session 1 violated rule 1 and 3 ("docketing specialist at a national law
# firm ... our staff ... filing in this district daily"); session 2
# over-corrected by banning the true profession outright. This lint enforces
# the three real rules instead.
EMPLOYER_ATTRIBUTION_PHRASES = [
    "[firm name]",
    "national law firm",
    "a national firm",
    "my firm",
    "our firm",
    "the firm i work",
    "my employer",
    "on behalf of my employer",
    "firm letterhead",
    "i support attorneys filing",
]

IN_USE_CLAIM_PHRASES = [
    "operating today",
    "in production use",
    "in daily use",
    "in use since",
    "our staff",
    "used by attorneys",
    "attorneys rely on",
    "has filed for",
    "files for clients",
]

# Words that may only appear in a letter body as part of an allowed phrase.
import re

PLURAL_VOICE_RE = re.compile(r"\b(we|our|us)\b")

# Lines where first-person plural is legitimately not Jackson's voice:
# quoted court/form labels, quotes from official documents, and named-entity
# constructions. Keep this list short and literal.
PLURAL_ALLOWED_SUBSTRINGS = [
    "how can we assist you",  # the M.D. Fla. web form's own field label
    "> the undersigned",  # quoted declaration text from the FL application form
]


# Everything after this marker in a draft is editorial commentary — the
# "why this reads the way it does" notes — not text that gets sent. Those
# notes are allowed to quote the retired framing in order to explain it.
NOTES_MARKER = "<!-- lint:notes -->"


def _letter_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text.split(NOTES_MARKER, 1)[0].lower()


def test_outreach_no_employer_attribution() -> None:
    violations: list[str] = []
    for path in _outreach_files():
        body = _letter_body(path)
        for phrase in EMPLOYER_ATTRIBUTION_PHRASES:
            if phrase in body:
                violations.append(f"{path.relative_to(REPO)}: '{phrase}'")
    assert violations == [], (
        "Employer named or implicated in outbound correspondence:\n"
        + "\n".join(violations)
        + f"\n(Editorial notes may discuss it below a {NOTES_MARKER} marker.)"
    )


def test_outreach_no_in_use_claims() -> None:
    violations: list[str] = []
    for path in _outreach_files():
        body = _letter_body(path)
        for phrase in IN_USE_CLAIM_PHRASES:
            if phrase in body:
                violations.append(f"{path.relative_to(REPO)}: '{phrase}'")
    assert violations == [], (
        "ECFiler-in-use claim in outbound correspondence (it has never filed "
        "for a client):\n" + "\n".join(violations)
    )


def test_outreach_singular_voice() -> None:
    """No organizational 'we/our/us' in letter bodies — there is one person."""
    violations: list[str] = []
    for path in _outreach_files():
        body = _letter_body(path)
        for lineno, line in enumerate(body.splitlines(), start=1):
            if any(allowed in line for allowed in PLURAL_ALLOWED_SUBSTRINGS):
                continue
            m = PLURAL_VOICE_RE.search(line)
            if m:
                violations.append(
                    f"{path.relative_to(REPO)}:{lineno}: '{m.group(0)}' in: "
                    f"{line.strip()[:80]}"
                )
    assert violations == [], (
        "Organizational voice in outbound correspondence:\n"
        + "\n".join(violations)
        + f"\n(Editorial notes below {NOTES_MARKER} are exempt; quoted form "
        "labels can be allowlisted in PLURAL_ALLOWED_SUBSTRINGS.)"
    )


def test_demo_is_labeled_scripted() -> None:
    """The landing-page walkthrough is an animation and must say so.

    Session 2 found the demo rendering a "Connected" status chip over a
    synthetic animation; session 4 relabeled it. The label stays, the fake
    connection-status language stays gone.
    """
    demo = (REPO / "web" / "components" / "demo.tsx").read_text(encoding="utf-8")
    assert "Scripted demo" in demo, "demo.tsx lost its 'Scripted demo' label"
    assert "Connected" not in demo, (
        "demo.tsx renders a connection-status chip again — it is a scripted "
        "animation, not a live connection"
    )
    landing = (REPO / "web" / "app" / "page.tsx").read_text(encoding="utf-8")
    assert "Live Demo" not in landing, (
        "landing page calls the scripted walkthrough a 'Live Demo' again"
    )


def test_court_count_single_source() -> None:
    """The wrong court counts (150 / 94-43-13 breakdown) must not reappear."""
    stale = ["150 federal courts", "43 bankruptcy", "13 appellate"]
    for path in _files():
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in stale:
            assert phrase not in text, f"stale court count in {path.relative_to(REPO)}: '{phrase}'"
