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

    def test_has_district_courts(self) -> None:
        district = self.registry.list_courts("district")
        assert len(district) >= 94  # 94 standard + special courts (JPML, CIT, COFC)

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


class _FakeElement:
    def __init__(self) -> None:
        self.checked = False

    def check(self) -> None:
        self.checked = True


class _FakePage:
    """Minimal Playwright Page stub for fee-status selector tests."""

    def __init__(
        self,
        present_selectors: dict[str, _FakeElement] | None = None,
        select_option_fail_by_value: bool = False,
        select_option_fail_all: bool = False,
    ) -> None:
        self.present = present_selectors or {}
        self.select_option_calls: list[dict] = []
        self.select_option_fail_by_value = select_option_fail_by_value
        self.select_option_fail_all = select_option_fail_all

    def query_selector(self, selector: str) -> _FakeElement | None:
        return self.present.get(selector)

    def select_option(self, selector: str, value=None, label=None):
        self.select_option_calls.append({"selector": selector, "value": value, "label": label})
        if self.select_option_fail_all:
            raise RuntimeError("no matching option")
        if self.select_option_fail_by_value and value is not None:
            raise RuntimeError("no matching value")
        return None


class TestFeeStatusSelection:
    def _court(self, fee_options=None, radios=None, fee_status_selector="select[name='fee_status']"):
        selectors = CourtSelectors()
        selectors.fee_status = fee_status_selector
        if fee_options is not None:
            selectors.fee_status_options = fee_options
        if radios is not None:
            selectors.fee_status_radios = radios
        profile = CourtProfile(
            court_id="test",
            name="Test",
            court_type="district",
            ecf_url="https://ecf.test.uscourts.gov",
            selectors=selectors,
        )
        return BaseCourt(profile)

    def test_default_uses_lowercase_value(self) -> None:
        court = self._court()
        el = _FakeElement()
        page = _FakePage(present_selectors={"select[name='fee_status']": el})
        court.select_fee_status(page, "ifp")
        assert page.select_option_calls == [
            {"selector": "select[name='fee_status']", "value": "ifp", "label": None}
        ]

    def test_per_court_override_value(self) -> None:
        court = self._court(fee_options={"paid": "Paid", "waived": "Waived", "ifp": "In Forma Pauperis"})
        el = _FakeElement()
        page = _FakePage(present_selectors={"select[name='fee_status']": el})
        court.select_fee_status(page, "ifp")
        assert page.select_option_calls[0]["value"] == "In Forma Pauperis"

    def test_label_fallback_when_value_fails(self) -> None:
        court = self._court(fee_options={"paid": "Paid", "waived": "Waived", "ifp": "In Forma Pauperis"})
        el = _FakeElement()
        page = _FakePage(
            present_selectors={"select[name='fee_status']": el},
            select_option_fail_by_value=True,
        )
        court.select_fee_status(page, "ifp")
        assert len(page.select_option_calls) == 2
        assert page.select_option_calls[1]["label"] == "In Forma Pauperis"

    def test_radio_override_used_when_no_dropdown(self) -> None:
        court = self._court(radios={"ifp": "input[value='IFP']"})
        radio = _FakeElement()
        page = _FakePage(present_selectors={"input[value='IFP']": radio})
        court.select_fee_status(page, "ifp")
        assert radio.checked

    def test_missing_control_logs_warning_and_returns(self, caplog) -> None:
        import logging

        court = self._court()
        page = _FakePage(present_selectors={})
        with caplog.at_level(logging.WARNING, logger="ecfiler.courts.base"):
            court.select_fee_status(page, "ifp")
        assert any("Fee status control not found" in rec.message for rec in caplog.records)

    def test_unknown_status_is_ignored(self, caplog) -> None:
        import logging

        court = self._court()
        el = _FakeElement()
        page = _FakePage(present_selectors={"select[name='fee_status']": el})
        with caplog.at_level(logging.WARNING, logger="ecfiler.courts.base"):
            court.select_fee_status(page, "bogus")
        assert page.select_option_calls == []

    def test_registered_court_has_fee_status_override(self) -> None:
        registry = CourtRegistry()
        nysd = registry.get("nysd")
        assert nysd.selectors.fee_status_options.get("ifp") == "In Forma Pauperis"

    def test_registered_court_without_override_uses_default(self) -> None:
        registry = CourtRegistry()
        court = registry.get("akd")
        assert court.selectors.fee_status_options == {"paid": "paid", "waived": "waived", "ifp": "ifp"}
