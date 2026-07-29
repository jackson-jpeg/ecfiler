"""Court registry — lookup and instantiation of court profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ecfiler.courts.appellate import AppellateCourt
from ecfiler.courts.bankruptcy import BankruptcyCourt
from ecfiler.courts.base import BaseCourt, CourtProfile, CourtSelectors
from ecfiler.courts.district import DistrictCourt

DATA_DIR = Path(__file__).parent / "data"

# Court class mapping by type
COURT_CLASSES: dict[str, type[BaseCourt]] = {
    "district": DistrictCourt,
    "bankruptcy": BankruptcyCourt,
    "appellate": AppellateCourt,
}


class CourtNotFoundError(Exception):
    """Raised when a court ID is not in the registry."""


class CourtEnvironmentError(CourtNotFoundError):
    """Raised when a court ID exists only in the *other* PACER environment.

    A QA/test court can never be served in production mode and a production
    court can never be served in QA mode — this is the structural guarantee
    that a QA package cannot reach a production endpoint (and vice versa),
    enforced at lookup rather than by convention.
    """


def active_environment() -> str:
    """The PACER environment this process is in: "qa" or "production".

    Driven by ECFILER_PACER_QA=1 — the same switch that selects the QA
    cso-auth realm, so the court directory and the credential realm can
    never disagree.
    """
    import os

    return "qa" if os.environ.get("ECFILER_PACER_QA", "") == "1" else "production"


class CourtRegistry:
    """Registry of federal courts for exactly one PACER environment.

    Loads court configurations from JSON data files and instantiates the
    appropriate court class. Courts belonging to the other environment are
    tracked by ID only, so lookups can fail with a precise error instead of
    silently resolving a QA court in production (or the reverse).
    """

    def __init__(self, environment: str | None = None) -> None:
        self.environment = environment or active_environment()
        if self.environment not in ("production", "qa"):
            raise ValueError(f"Unknown court environment: {self.environment!r}")
        self._courts: dict[str, dict[str, Any]] = {}
        self._other_environment: dict[str, str] = {}  # court_id -> its env
        self._load_all()

    def _load_all(self) -> None:
        """Load all court data files, keeping only the active environment."""
        for json_file in DATA_DIR.glob("*_courts.json"):
            try:
                with open(json_file) as f:
                    courts = json.load(f)
                for court_data in courts:
                    court_id = court_data["court_id"]
                    env = court_data.get("environment", "production")
                    if env == self.environment:
                        self._courts[court_id] = court_data
                    else:
                        self._other_environment[court_id] = env
            except (json.JSONDecodeError, KeyError) as e:
                # Skip malformed data files
                import sys

                print(f"Warning: Could not load {json_file}: {e}", file=sys.stderr)

    def get(self, court_id: str) -> BaseCourt:
        """Get a court instance by ID.

        Args:
            court_id: Court identifier (e.g., "nysd", "cacb", "ca2")

        Returns:
            Appropriate court subclass instance

        Raises:
            CourtEnvironmentError: If the court exists only in the other
                PACER environment (QA court in production mode or vice versa)
            CourtNotFoundError: If court ID is not found at all
        """
        data = self._courts.get(court_id)
        if data is None:
            other = self._other_environment.get(court_id)
            if other is not None:
                raise CourtEnvironmentError(
                    f"Court '{court_id}' is a {other} court but this run is in "
                    f"{self.environment} mode — refusing to file across PACER "
                    f"environments. (QA mode is ECFILER_PACER_QA=1.)"
                )
            raise CourtNotFoundError(
                f"Court '{court_id}' not found. "
                f"Use 'list' to see available courts."
            )

        court_type = data.get("court_type", "district")
        court_class = COURT_CLASSES.get(court_type, BaseCourt)
        return court_class.from_dict(data)

    def list_courts(self, court_type: str | None = None) -> list[dict[str, str]]:
        """List all available courts.

        Args:
            court_type: Optional filter by type (district/bankruptcy/appellate)

        Returns:
            List of {"court_id": "...", "name": "...", "type": "..."} dicts
        """
        courts = []
        for court_id, data in sorted(self._courts.items()):
            ct = data.get("court_type", "district")
            if court_type and ct != court_type:
                continue
            courts.append({
                "court_id": court_id,
                "name": data.get("name", court_id),
                "type": ct,
            })
        return courts

    def search(self, query: str) -> list[dict[str, str]]:
        """Search courts by name or ID.

        Args:
            query: Search string (matches against ID and name)

        Returns:
            Matching courts
        """
        query_lower = query.lower().strip()
        words = query_lower.split()
        results = []
        for court_id, data in self._courts.items():
            name = data.get("name", "")
            # The ECF hostname is searchable too: filers know courts by the
            # host they log into (a QA filer types "tc1d", not "azttdc").
            searchable = f"{court_id} {name} {data.get('ecf_url', '')}".lower()
            # Match if all words appear in the court ID + name
            if all(w in searchable for w in words):
                results.append({
                    "court_id": court_id,
                    "name": name,
                    "type": data.get("court_type", "district"),
                })
        # Sort: exact ID match first, then by name
        results.sort(key=lambda c: (0 if c["court_id"].lower() == query_lower else 1, c["name"]))
        return results

    @property
    def count(self) -> int:
        return len(self._courts)
