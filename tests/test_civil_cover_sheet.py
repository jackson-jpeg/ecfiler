"""Tests for civil cover sheet (JS-44) data."""

import pytest

from ecfiler.filing.civil_cover_sheet import (
    CivilCoverSheet,
    get_nature_of_suit_categories,
    get_nature_of_suit_codes,
    search_nature_of_suit,
)


class TestNatureOfSuit:
    def test_categories_exist(self) -> None:
        cats = get_nature_of_suit_categories()
        assert len(cats) >= 10
        assert "Contract" in cats
        assert "Civil Rights" in cats
        assert "Intellectual Property" in cats
        assert "Labor" in cats

    def test_get_all_codes(self) -> None:
        codes = get_nature_of_suit_codes()
        assert len(codes) >= 80
        # Each code should have code, description, category
        for c in codes:
            assert "code" in c
            assert "description" in c
            assert "category" in c

    def test_get_codes_by_category(self) -> None:
        codes = get_nature_of_suit_codes("Civil Rights")
        assert len(codes) >= 5
        assert any(c["code"] == "442" for c in codes)  # Employment

    def test_get_codes_invalid_category(self) -> None:
        codes = get_nature_of_suit_codes("Nonexistent")
        assert codes == []

    def test_search_by_description(self) -> None:
        results = search_nature_of_suit("employment")
        assert len(results) >= 1
        assert any("Employment" in r["description"] for r in results)

    def test_search_by_category(self) -> None:
        results = search_nature_of_suit("intellectual")
        assert len(results) >= 3  # Copyright, Patent, Trademark at minimum

    def test_search_no_results(self) -> None:
        results = search_nature_of_suit("xyznonexistent")
        assert len(results) == 0

    def test_known_codes_exist(self) -> None:
        """Verify specific well-known NOS codes are present."""
        all_codes = get_nature_of_suit_codes()
        code_map = {c["code"]: c["description"] for c in all_codes}

        assert "110" in code_map  # Insurance
        assert "350" in code_map  # Motor Vehicle
        assert "440" in code_map  # Other Civil Rights
        assert "830" in code_map  # Patent
        assert "820" in code_map  # Copyrights


class TestCivilCoverSheet:
    def test_default_values(self) -> None:
        sheet = CivilCoverSheet()
        assert sheet.nature_of_suit_code == ""
        assert sheet.class_action is False

    def test_populated_sheet(self) -> None:
        sheet = CivilCoverSheet(
            nature_of_suit_code="442",
            nature_of_suit_description="Employment",
            jurisdiction_basis="3",
            cause_of_action_statute="42 USC 1983",
            jury_demand="plaintiff",
        )
        assert sheet.nature_of_suit_code == "442"
        assert sheet.jury_demand == "plaintiff"


class TestNatureOfSuitAPI:
    """Test the API endpoints via TestClient."""

    def test_list_nos(self) -> None:
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)
        response = client.get("/api/nature-of-suit")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 80

    def test_filter_by_category(self) -> None:
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)
        response = client.get("/api/nature-of-suit?category=Labor")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3

    def test_search_nos(self) -> None:
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)
        response = client.get("/api/nature-of-suit?search=patent")
        assert response.status_code == 200
        data = response.json()
        assert any("Patent" in d["description"] for d in data)

    def test_categories_endpoint(self) -> None:
        from fastapi.testclient import TestClient
        from ecfiler.api.app import app

        client = TestClient(app)
        response = client.get("/api/nature-of-suit/categories")
        assert response.status_code == 200
        cats = response.json()
        assert "Contract" in cats
