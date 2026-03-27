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


class CourtRegistry:
    """Registry of all known federal courts.

    Loads court configurations from JSON data files and
    instantiates the appropriate court class.
    """

    def __init__(self) -> None:
        self._courts: dict[str, dict[str, Any]] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Load all court data files."""
        for json_file in DATA_DIR.glob("*_courts.json"):
            try:
                with open(json_file) as f:
                    courts = json.load(f)
                for court_data in courts:
                    court_id = court_data["court_id"]
                    self._courts[court_id] = court_data
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
            CourtNotFoundError: If court ID is not found
        """
        data = self._courts.get(court_id)
        if data is None:
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
        query_lower = query.lower()
        results = []
        for court_id, data in self._courts.items():
            name = data.get("name", "")
            if query_lower in court_id.lower() or query_lower in name.lower():
                results.append({
                    "court_id": court_id,
                    "name": name,
                    "type": data.get("court_type", "district"),
                })
        return results

    @property
    def count(self) -> int:
        return len(self._courts)
