"""docs/verification-ledger.md is the only home for verification claims.

Session 3 wrote "production redeployed … verified from an external browser"
with no evidence behind it, and the claim was false when measured. The
ledger is where evidence lives; these tests make the discipline mechanical:

- ledger rows are well-formed (id, date, a [VPS]/[MAC]-labeled command or a
  public CI reference, and a VERIFIED/STAGED/UNPROVEN status) and their ids
  never renumber (append-only);
- in the governed docs, any affirmative "proven"/"verified" sentence must
  carry its backing — a ledger row ref, a tests/ path, or the command that
  reproduces it;
- the exact phrase class that burned us ("verified from an external
  browser") may not appear outside the ledger at all.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = REPO / "docs" / "verification-ledger.md"

GOVERNED_DOCS = [
    "docs/hosting-topology.md",
    "docs/nef-roundtrip-runbook.md",
    "docs/risk-register.md",
    "HUMAN-QUEUE.md",
]

STATUSES = {"VERIFIED", "STAGED", "UNPROVEN"}

# A "proven"/"verified" line is backed when it cites one of these.
BACKING_RE = re.compile(
    r"\(L\d\d|ledger|tests/|make qa-day|GitHub Actions|scripts/verify-production\.sh|CI",
)
# Negative/future/conditional uses assert nothing and need no backing.
NEGATION_RE = re.compile(
    r"\bnot\b|\byet\b|\buntil\b|\bunproven\b|\bremains\b|\bwould\b|\bonce\b|\bwhen\b|\bstops being\b",
    re.IGNORECASE,
)
CLAIM_RE = re.compile(r"\b(proven|verified|re-verified)\b", re.IGNORECASE)


def _ledger_rows() -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    current_id: int | None = None
    current: list[str] = []
    for line in LEDGER.read_text(encoding="utf-8").splitlines():
        m = re.match(r"### L(\d+) — ", line)
        if m:
            if current_id is not None:
                rows.append((current_id, "\n".join(current)))
            current_id = int(m.group(1))
            current = [line]
        elif current_id is not None:
            if line.startswith("---"):
                rows.append((current_id, "\n".join(current)))
                current_id = None
                current = []
            else:
                current.append(line)
    if current_id is not None:
        rows.append((current_id, "\n".join(current)))
    return rows


def test_ledger_exists_with_rows() -> None:
    assert LEDGER.is_file()
    assert len(_ledger_rows()) >= 12


def test_ledger_ids_are_append_only() -> None:
    ids = [i for i, _ in _ledger_rows()]
    assert ids == sorted(ids), "ledger row ids must never renumber"
    assert len(ids) == len(set(ids)), "duplicate ledger row id"


def test_ledger_rows_carry_evidence_and_status() -> None:
    problems: list[str] = []
    for row_id, body in _ledger_rows():
        if not re.search(r"\[(VPS|MAC)\]|GitHub Actions|GitHub deployment", body):
            problems.append(f"L{row_id:02d}: no [VPS]/[MAC] command or CI reference")
        if not re.search(r"\b20\d\d-\d\d-\d\d\b", body):
            problems.append(f"L{row_id:02d}: no date")
        if not any(s in body for s in STATUSES):
            problems.append(f"L{row_id:02d}: no VERIFIED/STAGED/UNPROVEN status")
    assert problems == [], "\n".join(problems)


def test_retro_audit_table_uses_valid_statuses() -> None:
    text = LEDGER.read_text(encoding="utf-8")
    audit = text.split("## Retro-audit", 1)[1]
    rows = [l for l in audit.splitlines() if l.startswith("| ") and "---" not in l]
    assert len(rows) >= 15
    for row in rows[1:]:
        assert any(s in row for s in STATUSES), f"no status in: {row[:70]}"


def test_governed_docs_back_their_verification_claims() -> None:
    violations: list[str] = []
    for relpath in GOVERNED_DOCS:
        path = REPO / relpath
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not CLAIM_RE.search(line):
                continue
            if NEGATION_RE.search(line):
                continue
            if BACKING_RE.search(line):
                continue
            violations.append(f"{relpath}:{lineno}: {line.strip()[:80]}")
    assert violations == [], (
        "Affirmative verification claims without backing (cite a ledger row, "
        "a tests/ path, or the reproducing command):\n" + "\n".join(violations)
    )


def test_burned_phrase_lives_only_in_the_ledger() -> None:
    pattern = re.compile(r"(verified|confirmed) from an external", re.IGNORECASE)
    offenders = []
    for path in REPO.glob("docs/**/*.md"):
        if path == LEDGER:
            continue
        if pattern.search(path.read_text(encoding="utf-8", errors="ignore")):
            offenders.append(str(path.relative_to(REPO)))
    for name in ("HUMAN-QUEUE.md", "README.md", "BRANDING.md"):
        if pattern.search((REPO / name).read_text(encoding="utf-8")):
            offenders.append(name)
    assert offenders == [], (
        "'verified from an external …' outside the ledger — that phrase "
        "requires ledger evidence: " + ", ".join(offenders)
    )
