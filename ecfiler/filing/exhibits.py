"""Exhibit and attachment management for CM/ECF filings.

Many filings include a main document plus multiple exhibits/attachments.
CM/ECF requires each to be:
- A separate PDF file
- Individually labeled (Exhibit A, Exhibit B, or Exhibit 1, 2, 3)
- Named with a description
- Uploaded in order

This module handles labeling, ordering, and validation of exhibit packages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class LabelStyle(str, Enum):
    """How exhibits are labeled."""
    LETTER = "letter"  # Exhibit A, B, C...
    NUMBER = "number"  # Exhibit 1, 2, 3...
    CUSTOM = "custom"  # Custom label per exhibit


MAX_EXHIBIT_BYTES = 100 * 1024 * 1024  # 100 MB — CM/ECF default per-file cap


@dataclass
class Exhibit:
    """A single exhibit or attachment."""
    file_path: str
    label: str = ""  # e.g., "Exhibit A" or "Attachment 1"
    description: str = ""  # e.g., "Contract dated January 1, 2024"
    order: int = 0
    sealed: bool = False

    @property
    def filename(self) -> str:
        return Path(self.file_path).name

    @property
    def size_bytes(self) -> int:
        p = Path(self.file_path)
        return p.stat().st_size if p.exists() else 0

    @property
    def display_name(self) -> str:
        parts = []
        if self.label:
            parts.append(self.label)
        if self.description:
            parts.append(self.description)
        return " — ".join(parts) if parts else self.filename


@dataclass
class ExhibitPackage:
    """A complete filing package with main document + exhibits."""
    main_document: str  # Path to the main document
    main_description: str = ""
    exhibits: list[Exhibit] = field(default_factory=list)
    label_style: LabelStyle = LabelStyle.LETTER

    @property
    def total_files(self) -> int:
        return 1 + len(self.exhibits)

    @property
    def exhibit_count(self) -> int:
        return len(self.exhibits)

    @property
    def has_sealed_exhibits(self) -> bool:
        return any(e.sealed for e in self.exhibits)

    def add_exhibit(self, file_path: str, description: str = "", sealed: bool = False) -> Exhibit:
        """Add an exhibit and auto-assign a label."""
        order = len(self.exhibits)
        label = self._next_label(order)
        exhibit = Exhibit(
            file_path=file_path,
            label=label,
            description=description,
            order=order,
            sealed=sealed,
        )
        self.exhibits.append(exhibit)
        return exhibit

    def reorder(self, new_order: list[int]) -> None:
        """Reorder exhibits by their indices."""
        self.exhibits = [self.exhibits[i] for i in new_order]
        self._relabel()

    def remove(self, index: int) -> None:
        """Remove an exhibit by index and relabel."""
        self.exhibits.pop(index)
        self._relabel()

    def _next_label(self, index: int) -> str:
        if self.label_style == LabelStyle.LETTER:
            if index < 26:
                return f"Exhibit {chr(65 + index)}"
            return f"Exhibit {chr(65 + index // 26 - 1)}{chr(65 + index % 26)}"
        elif self.label_style == LabelStyle.NUMBER:
            return f"Exhibit {index + 1}"
        return ""

    def _relabel(self) -> None:
        for i, exhibit in enumerate(self.exhibits):
            exhibit.order = i
            if self.label_style != LabelStyle.CUSTOM:
                exhibit.label = self._next_label(i)

    def validate(self) -> list[str]:
        """Validate the exhibit package. Returns list of issues."""
        issues = []
        if not Path(self.main_document).exists():
            issues.append(f"Main document not found: {self.main_document}")

        for ex in self.exhibits:
            path = Path(ex.file_path)
            if not path.exists():
                issues.append(f"{ex.label}: File not found: {ex.file_path}")
            else:
                size = path.stat().st_size
                if size > MAX_EXHIBIT_BYTES:
                    issues.append(
                        f"{ex.label}: File too large ({size / 1024 / 1024:.1f}MB, max {MAX_EXHIBIT_BYTES // 1024 // 1024}MB)"
                    )
            if not ex.description:
                issues.append(f"{ex.label}: Missing description (CM/ECF may require one)")

        # Check for duplicates
        paths = [self.main_document] + [e.file_path for e in self.exhibits]
        if len(paths) != len(set(paths)):
            issues.append("Duplicate files detected in exhibit package")

        return issues


def create_package(
    main_document: str,
    exhibit_files: list[str],
    descriptions: list[str] | None = None,
    label_style: LabelStyle = LabelStyle.LETTER,
) -> ExhibitPackage:
    """Create an exhibit package from a main document and list of exhibit files.

    Args:
        main_document: Path to the main filing document
        exhibit_files: Paths to exhibit/attachment files
        descriptions: Optional descriptions for each exhibit
        label_style: How to label exhibits (letter, number, custom)

    Returns:
        ExhibitPackage ready for filing
    """
    package = ExhibitPackage(
        main_document=main_document,
        label_style=label_style,
    )

    descs = descriptions or [""] * len(exhibit_files)
    for path, desc in zip(exhibit_files, descs):
        package.add_exhibit(path, desc)

    return package


def package_from_metadata(
    main_document: str,
    exhibits: list[dict],
    label_style: LabelStyle = LabelStyle.LETTER,
) -> ExhibitPackage:
    """Build an ExhibitPackage from a list of {file_path, description, sealed} dicts.

    Preserves the order of the input list (labels auto-assigned A/B/C or 1/2/3).
    """
    package = ExhibitPackage(main_document=main_document, label_style=label_style)
    for item in exhibits:
        package.add_exhibit(
            item.get("file_path", "") or item.get("name", ""),
            item.get("description", ""),
            sealed=bool(item.get("sealed", False)),
        )
    return package

    return package
