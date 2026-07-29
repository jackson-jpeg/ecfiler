"""docs/claims-register.md is enforced, not aspirational.

Every outward-facing factual claim must have a register row mapping it to
implementing code and a proving test. This module makes the register
load-bearing:

- register rows can't rot (quoted claims must still appear in their files,
  cited tests must exist, FALSE verdicts are release blockers);
- new claims can't ship unregistered (a signature sweep over every public
  surface fails on claim-bearing strings with no covering row);
- the numeric literals that survive on public surfaces are pinned to their
  Python sources (court counts, fee amounts, retention days, safety gates).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
REGISTER = REPO / "docs" / "claims-register.md"

VALID_VERDICTS = {"TRUE", "TRUE-BUT-UNREACHABLE", "ASPIRATIONAL", "FALSE"}

# Public surfaces swept for claim signatures. Deliberately excludes web/lib
# code files other than facts.ts — code comments are not user-visible copy;
# facts.ts strings render verbatim in the UI.
def _sweep_files() -> list[Path]:
    out: list[Path] = []
    for pattern in ("web/app/**/*.tsx", "web/components/*.tsx"):
        out.extend(REPO.glob(pattern))
    out.append(REPO / "web" / "lib" / "facts.ts")
    out.append(REPO / "README.md")
    out.append(REPO / "BRANDING.md")
    return [p for p in out if p.is_file()]


# Signature → token that must appear in some register row for the file.
# A signature marks a string as claim-bearing; the token check ties it to a
# row without requiring rows to quote every repetition.
CLAIM_SIGNATURES: list[tuple[re.Pattern, str]] = [
    (re.compile(r"\b\d+ safety gates"), "safety gates"),
    (re.compile(r"\b(?:\d+|five|three|seven)-point", re.IGNORECASE), "-point"),
    (re.compile(r"\b\d-pass\b"), "-pass"),
    (re.compile(r"stripe", re.IGNORECASE), "stripe"),
    (re.compile(r"\$\d[\d,.]*"), "$"),
    (re.compile(r"\b\d+ federal courts"), "federal courts"),
    (
        re.compile(
            r"never (?:sees?|holds?|held|touch(?:es)?|reach(?:es)?|leaves?|uploaded)",
            re.IGNORECASE,
        ),
        "never",
    ),
    (re.compile(r"append-only", re.IGNORECASE), "append-only"),
    (re.compile(r"Rule 5\.2", re.IGNORECASE), "rule 5.2"),
    (re.compile(r"PDF/A"), "pdf/a"),
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).lower()


class Row:
    def __init__(self, cells: list[str]):
        self.claim = cells[0].strip()
        self.surface = cells[1].strip()
        self.impl = cells[2].strip()
        self.tests = cells[3].strip()
        self.verdict = cells[4].strip()


def _rows() -> list[Row]:
    rows: list[Row] = []
    for line in REGISTER.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue
        if cells[0] in ("Claim", "---") or set(cells[0]) <= {"-"}:
            continue
        rows.append(Row(cells))
    return rows


def _rows_by_surface() -> dict[str, list[Row]]:
    grouped: dict[str, list[Row]] = {}
    for row in _rows():
        grouped.setdefault(row.surface, []).append(row)
    return grouped


def test_register_parses_and_has_rows() -> None:
    rows = _rows()
    assert len(rows) >= 40, "claims register looks truncated"


def test_verdicts_are_valid_and_no_false_claims_survive() -> None:
    bad = [r.claim[:60] for r in _rows() if r.verdict not in VALID_VERDICTS]
    assert bad == [], f"invalid verdicts: {bad}"
    false = [f"{r.surface}: {r.claim[:80]}" for r in _rows() if r.verdict == "FALSE"]
    assert false == [], (
        "FALSE claims are release blockers — fix the code or delete the "
        "claim:\n" + "\n".join(false)
    )


def test_quoted_claims_still_appear_on_their_surfaces() -> None:
    missing: list[str] = []
    for row in _rows():
        if not row.claim.startswith("`"):
            continue  # descriptive row; covered by the signature sweep
        quote = row.claim.split("`")[1]
        surface = REPO / row.surface
        assert surface.is_file(), f"register names missing file {row.surface}"
        if _norm(quote) not in _norm(surface.read_text(encoding="utf-8")):
            missing.append(f"{row.surface}: `{quote}`")
    assert missing == [], (
        "Register quotes no longer on their surfaces (update the register "
        "with the copy):\n" + "\n".join(missing)
    )


def test_cited_proving_tests_exist() -> None:
    missing: list[str] = []
    for row in _rows():
        for ref in re.findall(r"tests/\S+\.py(?:::\S+)?", row.tests):
            parts = ref.rstrip(";,").split("::")
            test_file = REPO / parts[0]
            if not test_file.is_file():
                missing.append(ref)
                continue
            if len(parts) > 1:
                name = parts[-1]
                if f"def {name}(" not in test_file.read_text(encoding="utf-8") and (
                    f"class {name}" not in test_file.read_text(encoding="utf-8")
                ):
                    missing.append(ref)
    assert missing == [], "register cites nonexistent tests:\n" + "\n".join(missing)


def test_every_claim_signature_has_a_register_row() -> None:
    grouped = _rows_by_surface()
    uncovered: list[str] = []
    for path in _sweep_files():
        rel = str(path.relative_to(REPO))
        text = path.read_text(encoding="utf-8", errors="ignore")
        row_text = _norm(" ".join(r.claim + " " + r.impl for r in grouped.get(rel, [])))
        for pattern, token in CLAIM_SIGNATURES:
            if pattern.search(text) and token not in row_text:
                uncovered.append(f"{rel}: matches {pattern.pattern!r}, no row with {token!r}")
    assert uncovered == [], (
        "Claim-bearing strings with no covering register row — add a row to "
        "docs/claims-register.md:\n" + "\n".join(uncovered)
    )


# ---- numeric literals pinned to their Python sources ----------------------


def _court_counts() -> dict[str, int]:
    data_dir = REPO / "ecfiler" / "courts" / "data"
    return {
        name: len(json.loads((data_dir / f"{name}_courts.json").read_text()))
        for name in ("district", "bankruptcy", "appellate")
    }


def test_no_hand_typed_court_counts() -> None:
    """No .tsx file may hand-type the court totals; they flow from facts.ts."""
    counts = _court_counts()
    total = sum(counts.values())
    # Lookarounds exclude decimals and SVG path data like "0.207.07".
    patterns = [
        re.compile(rf"(?<![\d.]){total}(?![\d.])"),
        re.compile(rf"(?<![\d.]){counts['district']} district"),
        re.compile(rf"(?<![\d.]){counts['bankruptcy']} bankruptcy"),
        re.compile(rf"(?<![\d.]){counts['appellate']} appellate"),
    ]
    violations: list[str] = []
    for path in REPO.glob("web/app/**/*.tsx"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            if pattern.search(text):
                violations.append(f"{path.relative_to(REPO)}: {pattern.pattern}")
    for path in REPO.glob("web/components/*.tsx"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in patterns:
            if pattern.search(text):
                violations.append(f"{path.relative_to(REPO)}: {pattern.pattern}")
    assert violations == [], (
        "Hand-typed court counts (use COURT_COUNT/COURT_BREAKDOWN or compute "
        "from courts-data):\n" + "\n".join(violations)
    )


def test_readme_court_counts_match_data() -> None:
    """Any 'N federal courts' in README/BRANDING must equal the data total."""
    counts = _court_counts()
    total = sum(counts.values())
    for name in ("README.md", "BRANDING.md"):
        text = (REPO / name).read_text(encoding="utf-8")
        for m in re.finditer(r"\b(\d+) federal courts", text):
            assert int(m.group(1)) == total, (
                f"{name} claims {m.group(1)} federal courts; data has {total}"
            )
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    m = re.search(r"(\d+) district, (\d+) bankruptcy, (\d+) appellate", readme)
    assert m, "README court breakdown line missing"
    assert (int(m.group(1)), int(m.group(2)), int(m.group(3))) == (
        counts["district"],
        counts["bankruptcy"],
        counts["appellate"],
    )


def test_cmecf_page_fee_literals_match_schedule() -> None:
    """what-is-cmecf's dollar figures are the fee schedule's, not copywriting."""
    from ecfiler.filing.fees import BANKRUPTCY_FEES, DISTRICT_FEES

    page = (
        REPO / "web" / "app" / "(marketing)" / "what-is-cmecf" / "page.tsx"
    ).read_text(encoding="utf-8")
    m = re.search(
        r"Complaints \(\$(\d+)\), appeals \(\$(\d+)\), bankruptcy \(\$(\d+)-\$([\d,]+)\)",
        page,
    )
    assert m, "fee sentence changed — update this test and the claims register"
    assert int(m.group(1)) == int(DISTRICT_FEES["complaint"].amount)
    assert int(m.group(2)) == int(DISTRICT_FEES["appeal"].amount)
    assert int(m.group(3)) == int(BANKRUPTCY_FEES["chapter7"].amount)
    assert int(m.group(4).replace(",", "")) == int(BANKRUPTCY_FEES["chapter11"].amount)


def test_retention_days_pinned_to_storage() -> None:
    import inspect

    from ecfiler.storage.history import compress_old_pdfs

    default_days = inspect.signature(compress_old_pdfs).parameters["days_old"].default
    facts = (REPO / "web" / "lib" / "facts.ts").read_text(encoding="utf-8")
    m = re.search(r"RETENTION_DAYS = (\d+)", facts)
    assert m, "RETENTION_DAYS missing from facts.ts"
    assert int(m.group(1)) == default_days, (
        f"facts.ts RETENTION_DAYS={m.group(1)} but storage compresses at "
        f"{default_days} days"
    )


def test_seven_safety_gates_pinned_to_workflow() -> None:
    workflow = (REPO / "ecfiler" / "filing" / "workflow.py").read_text(encoding="utf-8")
    gates = {int(n) for n in re.findall(r"Safety Gates? (\d)", workflow)}
    assert gates and max(gates) == 7, f"workflow defines gates {sorted(gates)}"
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    m = re.search(r"\*\*(\d+) safety gates\*\*", readme)
    assert m and int(m.group(1)) == 7, "README safety-gate count drifted"


def test_no_stripe_claims_without_stripe_code() -> None:
    """Billing claims require billing code. There is none; so no 'Stripe'."""
    package = json.loads((REPO / "web" / "package.json").read_text())
    has_stripe = any(
        "stripe" in dep.lower()
        for section in ("dependencies", "devDependencies")
        for dep in package.get(section, {})
    )
    if has_stripe:
        pytest.skip("Stripe dependency present — revisit the register instead")
    violations = [
        str(p.relative_to(REPO))
        for p in _sweep_files()
        if "stripe" in p.read_text(encoding="utf-8", errors="ignore").lower()
    ]
    assert violations == [], (
        "'Stripe' claimed on a public surface but no Stripe code exists:\n"
        + "\n".join(violations)
    )
