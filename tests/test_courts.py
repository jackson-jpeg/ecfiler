"""Tests for court registry and court profiles."""

import pytest

from ecfiler.courts.base import BaseCourt, CourtProfile, CourtSelectors, ECFFormError
from ecfiler.courts.district import DistrictCourt
from ecfiler.courts.bankruptcy import BankruptcyCourt
from ecfiler.courts.appellate import AppellateCourt
from ecfiler.courts.registry import CourtNotFoundError, CourtRegistry


class TestCourtRegistry:
    def setup_method(self) -> None:
        self.registry = CourtRegistry()

    def test_loads_all_court_types(self) -> None:
        courts = self.registry.list_courts()
        types = {c["type"] for c in courts}
        assert "district" in types
        assert "bankruptcy" in types
        assert "appellate" in types

    def test_has_94_district_courts(self) -> None:
        district = self.registry.list_courts("district")
        assert len(district) == 94

    def test_has_appellate_courts(self) -> None:
        appellate = self.registry.list_courts("appellate")
        assert len(appellate) >= 13

    def test_has_bankruptcy_courts(self) -> None:
        bankruptcy = self.registry.list_courts("bankruptcy")
        assert len(bankruptcy) >= 30

    def test_get_known_court(self) -> None:
        court = self.registry.get("nysd")
        assert isinstance(court, DistrictCourt)
        assert court.profile.name == "Southern District of New York"
        assert "uscourts.gov" in court.profile.ecf_url

    def test_get_bankruptcy_court(self) -> None:
        court = self.registry.get("nysb")
        assert isinstance(court, BankruptcyCourt)

    def test_get_appellate_court(self) -> None:
        court = self.registry.get("ca2")
        assert isinstance(court, AppellateCourt)

    def test_court_not_found(self) -> None:
        with pytest.raises(CourtNotFoundError):
            self.registry.get("nonexistent")

    def test_search_by_name(self) -> None:
        results = self.registry.search("new york")
        assert len(results) >= 2  # At least SDNY and EDNY
        names = [r["name"].lower() for r in results]
        assert any("new york" in n for n in names)

    def test_search_by_id(self) -> None:
        results = self.registry.search("cacd")
        assert len(results) >= 1
        assert results[0]["court_id"] == "cacd"

    def test_search_no_results(self) -> None:
        results = self.registry.search("zzzznonexistent")
        assert len(results) == 0

    def test_count(self) -> None:
        assert self.registry.count >= 150


class TestCourtProfile:
    def test_login_url(self) -> None:
        profile = CourtProfile(
            court_id="nysd",
            name="Test Court",
            court_type="district",
            ecf_url="https://ecf.nysd.uscourts.gov",
        )
        assert profile.login_url == "https://ecf.nysd.uscourts.gov/cgi-bin/login.pl"

    def test_domain(self) -> None:
        profile = CourtProfile(
            court_id="nysd",
            name="Test Court",
            court_type="district",
            ecf_url="https://ecf.nysd.uscourts.gov",
        )
        assert profile.domain == "ecf.nysd.uscourts.gov"

    def test_from_dict(self) -> None:
        data = {
            "court_id": "test",
            "name": "Test Court",
            "court_type": "district",
            "ecf_url": "https://ecf.test.uscourts.gov",
            "quirks": ["requires_consent"],
        }
        court = BaseCourt.from_dict(data)
        assert court.profile.court_id == "test"
        assert "requires_consent" in court.profile.quirks

    def test_custom_selectors(self) -> None:
        data = {
            "court_id": "test",
            "name": "Test Court",
            "ecf_url": "https://ecf.test.uscourts.gov",
            "selectors": {"case_number_input": "#custom_case_input"},
        }
        court = BaseCourt.from_dict(data)
        assert court.selectors.case_number_input == "#custom_case_input"
        # Other selectors should keep defaults
        assert court.selectors.file_upload == "input[type='file']"


class TestCourtSelectors:
    def test_default_selectors(self) -> None:
        s = CourtSelectors()
        assert "textarea" in s.docket_text
        assert s.fee_status == "select[name='fee_status']"
        assert s.case_number_input == "input[name='case_num']"
        assert "input[type='file']" in s.file_upload
        assert "Next" in s.next_button

    def test_custom_selectors_from_dict(self) -> None:
        data = {
            "court_id": "test",
            "name": "Test",
            "ecf_url": "https://ecf.test.uscourts.gov",
            "selectors": {
                "docket_text": "#custom_docket",
                "brief_notice": "#custom_notice",
            },
        }
        court = BaseCourt.from_dict(data)
        assert court.selectors.docket_text == "#custom_docket"
        assert court.selectors.brief_notice == "#custom_notice"
        # Unchanged defaults
        assert court.selectors.fee_status == "select[name='fee_status']"


class TestECFFormError:
    def test_error_is_exception(self) -> None:
        with pytest.raises(ECFFormError, match="test error"):
            raise ECFFormError("test error")


class TestBankruptcyCourt:
    def test_supports_xml_filing(self) -> None:
        profile = CourtProfile(
            court_id="nysb",
            name="Test",
            court_type="bankruptcy",
            ecf_url="https://ecf.nysb.uscourts.gov",
            quirks=["xml_case_opening"],
        )
        court = BankruptcyCourt(profile)
        assert court.supports_xml_filing

    def test_no_xml_support(self) -> None:
        profile = CourtProfile(
            court_id="test",
            name="Test",
            court_type="bankruptcy",
            ecf_url="https://ecf.test.uscourts.gov",
        )
        court = BankruptcyCourt(profile)
        assert not court.supports_xml_filing
