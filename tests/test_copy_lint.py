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


# Jackson is an independent software developer. He is not an attorney, not a
# paralegal, and not employed by a law firm. Earlier drafts of the outreach
# letters described him as "a docketing specialist at a national law firm" and
# asserted a filing practice ("our staff", "I support attorneys filing in this
# district daily") that does not exist. Those letters are addressed to a federal
# clerk's office, the Administrative Office, and the Florida E-Filing Authority;
# a fabricated professional identity in that correspondence is a far worse
# problem than any it was meant to solve. This lint keeps it from coming back.
FALSE_IDENTITY_PHRASES = [
    "docketing specialist",
    "[firm name]",
    "national law firm",
    "our firm",
    "our staff",
    "i support attorneys filing",
]


# Everything after this marker in a draft is editorial commentary — the
# "why this reads the way it does" notes — not text that gets sent. Those
# notes are allowed to quote the retired framing in order to explain it.
NOTES_MARKER = "<!-- lint:notes -->"


def _letter_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return text.split(NOTES_MARKER, 1)[0].lower()


def test_outreach_identity_is_truthful() -> None:
    violations: list[str] = []
    for path in _outreach_files():
        body = _letter_body(path)
        for phrase in FALSE_IDENTITY_PHRASES:
            if phrase in body:
                violations.append(f"{path.relative_to(REPO)}: '{phrase}'")
    assert violations == [], (
        "False professional identity in outbound correspondence:\n"
        + "\n".join(violations)
        + f"\n(Editorial notes may discuss it below a {NOTES_MARKER} marker.)"
    )


def test_court_count_single_source() -> None:
    """The wrong court counts (150 / 94-43-13 breakdown) must not reappear."""
    stale = ["150 federal courts", "43 bankruptcy", "13 appellate"]
    for path in _files():
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in stale:
            assert phrase not in text, f"stale court count in {path.relative_to(REPO)}: '{phrase}'"
