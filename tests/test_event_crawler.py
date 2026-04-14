"""Unit tests for event-catalog crawler.

The crawler's HTTP logic is exercised indirectly via mocked Playwright pages
rather than a live CM/ECF — the goal is to validate parsing of the two
common event-picker widgets (select/option and checkbox list) and the
grouping into the output schema.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ecfiler.browser.event_crawler import CrawledEvent, CrawlResult, EventCrawler
from ecfiler.courts.base import CourtProfile


@pytest.fixture
def profile() -> CourtProfile:
    return CourtProfile(
        court_id="nysd",
        name="S.D.N.Y.",
        court_type="district",
        ecf_url="https://ecf.nysd.uscourts.gov",
    )


@pytest.fixture
def crawler(profile: CourtProfile) -> EventCrawler:
    return EventCrawler(profile, session=MagicMock(), delay=0)


class TestTrainingUrl:
    def test_default_follows_ecf_train_convention(self, profile: CourtProfile) -> None:
        assert profile.training_login_url == "https://ecf-train.nysd.uscourts.gov/cgi-bin/login.pl"

    def test_explicit_override(self) -> None:
        p = CourtProfile(
            court_id="txed",
            name="E.D. Tex.",
            court_type="district",
            ecf_url="https://ecf.txed.uscourts.gov",
            training_db_url="https://txed-ecf-train.local",
        )
        assert p.training_login_url == "https://txed-ecf-train.local/cgi-bin/login.pl"


class TestEnumerateEvents:
    def test_select_option_widget(self, crawler: EventCrawler) -> None:
        page = MagicMock()
        opt1, opt2, opt3 = MagicMock(), MagicMock(), MagicMock()
        opt1.get_attribute.return_value = "mot"
        opt1.inner_text.return_value = "Motion to Dismiss"
        opt2.get_attribute.return_value = "ans"
        opt2.inner_text.return_value = "Answer"
        opt3.get_attribute.return_value = ""
        opt3.inner_text.return_value = "Select one"
        event_select = MagicMock()
        event_select.query_selector_all.return_value = [opt1, opt2, opt3]
        page.query_selector_all.side_effect = lambda sel: (
            [event_select] if "select" in sel and "event" in sel else []
        )

        pairs = crawler._enumerate_events_on_page(page, "https://base", "/cgi-bin/x.pl")
        assert ("mot", "Motion to Dismiss") in pairs
        assert ("ans", "Answer") in pairs
        assert len(pairs) == 2  # blank option dropped

    def test_checkbox_widget_with_labels(self, crawler: EventCrawler) -> None:
        page = MagicMock()
        cb = MagicMock()
        cb.get_attribute.side_effect = lambda a: {"value": "103", "name": "event", "id": "cb-103"}.get(a)
        label = MagicMock()
        label.inner_text.return_value = "Motion for Summary Judgment"
        page.query_selector_all.side_effect = lambda sel: (
            [cb] if sel == "input[type='checkbox']" else []
        )
        page.query_selector.return_value = label

        pairs = crawler._enumerate_events_on_page(page, "https://base", "/cgi-bin/x.pl")
        assert pairs == [("103", "Motion for Summary Judgment")]

    def test_checkbox_ignored_when_name_not_event(self, crawler: EventCrawler) -> None:
        page = MagicMock()
        cb = MagicMock()
        cb.get_attribute.side_effect = lambda a: {"value": "1", "name": "other"}.get(a)
        page.query_selector_all.side_effect = lambda sel: (
            [cb] if sel == "input[type='checkbox']" else []
        )
        pairs = crawler._enumerate_events_on_page(page, "https://base", "/cgi-bin/x.pl")
        assert pairs == []


class TestSchemaConversion:
    def test_groups_by_category_and_subcategory(self) -> None:
        r = CrawlResult(court_id="nysd", court_type="district", source_url="https://ecf-train.nysd.uscourts.gov")
        r.events = [
            CrawledEvent("mot", "Motion", "civil", "Motions"),
            CrawledEvent("ans", "Answer", "civil", "Responsive"),
            CrawledEvent("indict", "Indictment", "criminal", ""),
        ]
        schema = r.to_json_schema()
        assert schema["court_type"] == "district"
        assert "civil / Motions" in schema["categories"]
        assert "civil / Responsive" in schema["categories"]
        assert "criminal" in schema["categories"]
        assert schema["categories"]["civil / Motions"] == [{"code": "mot", "description": "Motion"}]


class TestMenusForCourtType:
    def test_district_has_civil_and_criminal(self, crawler: EventCrawler) -> None:
        menus = crawler._menus_for_court_type()
        assert "civil" in menus and "criminal" in menus

    def test_bankruptcy(self) -> None:
        p = CourtProfile(court_id="nysb", name="S.D.N.Y. Bankr.", court_type="bankruptcy", ecf_url="https://ecf.nysb.uscourts.gov")
        c = EventCrawler(p, session=MagicMock(), delay=0)
        menus = c._menus_for_court_type()
        assert "bankruptcy" in menus and "adversary" in menus

    def test_unknown_court_type_empty(self) -> None:
        p = CourtProfile(court_id="xx", name="Unknown", court_type="weird", ecf_url="https://x")
        c = EventCrawler(p, session=MagicMock(), delay=0)
        assert c._menus_for_court_type() == {}
