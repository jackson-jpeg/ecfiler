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


def test_no_extra_web_data_files():
    """Every JSON under web/lib/data must correspond to a Python source file."""
    expected = {str(Path(p)) for p in COURT_FILES + EVENT_FILES}
    actual = {
        str(f.relative_to(WEB_DATA))
        for f in WEB_DATA.rglob("*.json")
    }
    assert actual == expected
