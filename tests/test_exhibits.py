"""Tests for exhibit package model: labeling, reorder, sealed, size validation."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from ecfiler.filing.exhibits import (
    MAX_EXHIBIT_BYTES,
    Exhibit,
    ExhibitPackage,
    LabelStyle,
    create_package,
    package_from_metadata,
)


def _touch(path: str, size: int = 10) -> None:
    Path(path).write_bytes(b"x" * size)


class TestLabelAutoGen:
    def test_letters_abc(self) -> None:
        pkg = ExhibitPackage(main_document="m.pdf", label_style=LabelStyle.LETTER)
        pkg.add_exhibit("a.pdf", "first")
        pkg.add_exhibit("b.pdf", "second")
        pkg.add_exhibit("c.pdf", "third")
        assert [e.label for e in pkg.exhibits] == ["Exhibit A", "Exhibit B", "Exhibit C"]

    def test_numbers_123(self) -> None:
        pkg = ExhibitPackage(main_document="m.pdf", label_style=LabelStyle.NUMBER)
        pkg.add_exhibit("a.pdf", "first")
        pkg.add_exhibit("b.pdf", "second")
        pkg.add_exhibit("c.pdf", "third")
        assert [e.label for e in pkg.exhibits] == ["Exhibit 1", "Exhibit 2", "Exhibit 3"]


class TestReorder:
    def test_reorder_preserves_labels_in_sequence(self) -> None:
        pkg = ExhibitPackage(main_document="m.pdf", label_style=LabelStyle.LETTER)
        pkg.add_exhibit("a.pdf", "first")
        pkg.add_exhibit("b.pdf", "second")
        pkg.add_exhibit("c.pdf", "third")

        pkg.reorder([2, 0, 1])  # c, a, b

        assert [e.filename for e in pkg.exhibits] == ["c.pdf", "a.pdf", "b.pdf"]
        assert [e.label for e in pkg.exhibits] == ["Exhibit A", "Exhibit B", "Exhibit C"]
        # Descriptions travel with exhibits
        assert pkg.exhibits[0].description == "third"
        assert pkg.exhibits[1].description == "first"

    def test_remove_relabels(self) -> None:
        pkg = ExhibitPackage(main_document="m.pdf", label_style=LabelStyle.LETTER)
        pkg.add_exhibit("a.pdf", "a")
        pkg.add_exhibit("b.pdf", "b")
        pkg.add_exhibit("c.pdf", "c")
        pkg.remove(1)
        assert [e.filename for e in pkg.exhibits] == ["a.pdf", "c.pdf"]
        assert [e.label for e in pkg.exhibits] == ["Exhibit A", "Exhibit B"]


class TestSizeValidation:
    def test_oversize_exhibit_fails_validation(self, tmp_path: Path) -> None:
        main = tmp_path / "main.pdf"
        main.write_bytes(b"x" * 100)

        big = tmp_path / "big.pdf"
        # Sparse file, filesystem reports full size cheaply
        with open(big, "wb") as f:
            f.seek(MAX_EXHIBIT_BYTES + 1)
            f.write(b"\0")

        pkg = ExhibitPackage(main_document=str(main))
        pkg.add_exhibit(str(big), "huge")
        issues = pkg.validate()
        assert any("too large" in i.lower() for i in issues)

    def test_normal_size_passes(self, tmp_path: Path) -> None:
        main = tmp_path / "main.pdf"
        main.write_bytes(b"x" * 100)
        ex = tmp_path / "ex.pdf"
        ex.write_bytes(b"x" * 100)
        pkg = ExhibitPackage(main_document=str(main))
        pkg.add_exhibit(str(ex), "desc")
        issues = pkg.validate()
        assert not any("too large" in i.lower() for i in issues)


class TestSealedFlag:
    def test_sealed_flag_propagates(self) -> None:
        pkg = ExhibitPackage(main_document="m.pdf")
        pkg.add_exhibit("a.pdf", "a", sealed=False)
        pkg.add_exhibit("b.pdf", "b", sealed=True)
        assert pkg.has_sealed_exhibits is True
        assert pkg.exhibits[0].sealed is False
        assert pkg.exhibits[1].sealed is True

    def test_no_sealed_exhibits(self) -> None:
        pkg = ExhibitPackage(main_document="m.pdf")
        pkg.add_exhibit("a.pdf", "a")
        assert pkg.has_sealed_exhibits is False


class TestPackageFromMetadata:
    def test_builds_from_dicts(self) -> None:
        pkg = package_from_metadata(
            main_document="m.pdf",
            exhibits=[
                {"file_path": "x.pdf", "description": "X", "sealed": True},
                {"file_path": "y.pdf", "description": "Y"},
            ],
        )
        assert pkg.exhibit_count == 2
        assert pkg.exhibits[0].label == "Exhibit A"
        assert pkg.exhibits[0].sealed is True
        assert pkg.has_sealed_exhibits is True
