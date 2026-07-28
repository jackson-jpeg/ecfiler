"""The web app ships court and event-code data as static JSON copies.

The Python files under ecfiler/courts/data/ are the source of truth; the
copies under web/lib/data/ make the public site self-sufficient (the court
directory and event-code browser work with no API). These tests fail when
the copies drift, so an edit to either side forces a re-sync.
"""

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent
PY_DATA = REPO_ROOT / "ecfiler" / "courts" / "data"
WEB_DATA = REPO_ROOT / "web" / "lib" / "data"

COURT_FILES = ["district_courts.json", "bankruptcy_courts.json", "appellate_courts.json"]
EVENT_FILES = [
    "event_codes/common_district.json",
    "event_codes/common_bankruptcy.json",
    "event_codes/common_appellate.json",
]


@pytest.mark.parametrize("relpath", COURT_FILES + EVENT_FILES)
def test_web_copy_matches_python_source(relpath):
    py_file = PY_DATA / relpath
    web_file = WEB_DATA / relpath
    assert web_file.exists(), (
        f"web/lib/data/{relpath} is missing — copy it from ecfiler/courts/data/"
    )
    py_data = json.loads(py_file.read_text())
    web_data = json.loads(web_file.read_text())
    assert web_data == py_data, (
        f"web/lib/data/{relpath} has drifted from ecfiler/courts/data/{relpath} — "
        f"re-copy the source file"
    )


GENERATED_FILES = ["fees.json", "redaction_patterns.json"]


def test_facts_constants_match_data():
    """web/lib/facts.ts court constants are pinned to the shipped data.

    Every court number on the site flows from facts.ts or from the JSON
    itself; this test is what makes those constants claims instead of
    copywriting.
    """
    import re

    counts = {
        name: len(json.loads((PY_DATA / f"{name}_courts.json").read_text()))
        for name in ("district", "bankruptcy", "appellate")
    }
    facts = (REPO_ROOT / "web" / "lib" / "facts.ts").read_text()

    m = re.search(r"COURT_COUNT = (\d+)", facts)
    assert m, "COURT_COUNT missing from web/lib/facts.ts"
    assert int(m.group(1)) == sum(counts.values()), (
        f"facts.ts COURT_COUNT={m.group(1)} but the registry data has "
        f"{sum(counts.values())} courts"
    )

    for name, expected in counts.items():
        m = re.search(rf"{name}: (\d+)", facts)
        assert m, f"COURT_BREAKDOWN.{name} missing from web/lib/facts.ts"
        assert int(m.group(1)) == expected, (
            f"facts.ts COURT_BREAKDOWN.{name}={m.group(1)} but the registry "
            f"data has {expected}"
        )


def test_no_extra_web_data_files():
    """Every JSON under web/lib/data must correspond to a Python source file."""
    expected = {str(Path(p)) for p in COURT_FILES + EVENT_FILES + GENERATED_FILES}
    actual = {
        str(f.relative_to(WEB_DATA))
        for f in WEB_DATA.rglob("*.json")
    }
    assert actual == expected


def test_fees_json_matches_python_source():
    """web/lib/data/fees.json is an exact export of ecfiler/filing/fees.py.

    The client-side fee lookup (web/lib/fees.ts) reads this JSON; if the
    Python schedule changes, this test forces the re-export.
    """
    import dataclasses

    from ecfiler.filing.fees import APPELLATE_FEES, BANKRUPTCY_FEES, DISTRICT_FEES

    expected = {
        name: {k: dataclasses.asdict(v) for k, v in table.items()}
        for name, table in [
            ("district", DISTRICT_FEES),
            ("bankruptcy", BANKRUPTCY_FEES),
            ("appellate", APPELLATE_FEES),
        ]
    }
    actual = json.loads((WEB_DATA / "fees.json").read_text())
    assert actual == expected, (
        "web/lib/data/fees.json has drifted from ecfiler/filing/fees.py — "
        "re-export it (see the generation snippet in the file's git history)"
    )


def test_redaction_patterns_json_matches_python_source():
    """web/lib/data/redaction_patterns.json mirrors ecfiler/pdf/redaction_check.py.

    The client-side Rule 5.2 scan (web/lib/redaction.ts) compiles these
    patterns; drift here means the free tool and the server scan disagree.
    """
    import re

    from ecfiler.pdf import redaction_check as rc

    def enc(p: re.Pattern) -> dict:
        return {"source": p.pattern, "ignoreCase": bool(p.flags & re.IGNORECASE)}

    expected = {
        "ssn": [enc(p) for p in rc.SSN_PATTERNS],
        "account": [enc(p) for p in rc.ACCOUNT_PATTERNS],
        "dob": [enc(p) for p in rc.DOB_PATTERNS],
        "ein": [enc(p) for p in rc.EIN_PATTERNS],
        "ssn_context_words": rc.SSN_CONTEXT_WORDS,
        "ein_context_words": rc.EIN_CONTEXT_WORDS,
    }
    actual = json.loads((WEB_DATA / "redaction_patterns.json").read_text())
    assert actual == expected, (
        "web/lib/data/redaction_patterns.json has drifted from "
        "ecfiler/pdf/redaction_check.py — re-export it"
    )
