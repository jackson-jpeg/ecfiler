"""A PACER account that cannot file must be told so, in those words.

Session 7's live QA run reached the Az Test District Court, authenticated,
entered the case number, and then failed three times looking for
`#event_list`. The element was genuinely absent: the account holds read
access only, so CM/ECF served Query / Reports / Utilities / Help / Log Out
and no Civil or Criminal menu at all (ledger L20).

"Selector not found" and "you are not registered to file here" are different
answers, and only the second one is true. These tests pin the difference,
because the day a user's court registration has not come through is the day
they meet this message.
"""

from __future__ import annotations

import pytest

from ecfiler.browser.recovery import retry_on_error
from ecfiler.courts.base import BaseCourt, CourtProfile, NotAnEFilerError
from ecfiler.courts.bankruptcy import BankruptcyCourt
from ecfiler.courts.appellate import AppellateCourt
from ecfiler.courts.district import DistrictCourt

# The menu bar the QA account was actually served, read off the screenshots
# the run left behind (docs/qa-roundtrip/).
READ_ONLY_MENU = ["Query", "Reports", "Utilities", "Help", "Log Out"]
FILER_MENU = ["Civil", "Criminal", "Query", "Reports", "Utilities", "Log Out"]


class FakeAnchor:
    def __init__(self, text: str) -> None:
        self._text = text

    def inner_text(self) -> str:
        return self._text


class DetachedAnchor(FakeAnchor):
    """A node that goes away mid-read, as they do during navigation."""

    def inner_text(self) -> str:
        raise RuntimeError("Element is not attached to the DOM")


class FakePage:
    def __init__(self, anchor_texts: list[str], url: str = "https://ecf.tc1d.aztc.uscourts.gov/cgi-bin/iquery.pl") -> None:
        self._anchors = [
            t if isinstance(t, FakeAnchor) else FakeAnchor(t) for t in anchor_texts
        ]
        self.url = url

    def query_selector_all(self, selector: str):
        assert selector == "a"
        return self._anchors


def _court(court_id: str = "azttdc") -> DistrictCourt:
    return DistrictCourt(
        CourtProfile(
            court_id=court_id,
            name="Az Test District Court",
            court_type="district",
            ecf_url="https://ecf.tc1d.aztc.uscourts.gov",
            environment="qa",
        )
    )


class TestTheQaDayFailure:
    """The exact page the browser landed on, in a test."""

    def test_read_only_account_is_told_it_cannot_file(self) -> None:
        with pytest.raises(NotAnEFilerError) as e:
            _court().check_filing_entitlement(FakePage(READ_ONLY_MENU))
        message = str(e.value)
        assert "not registered to e-file" in message
        assert "azttdc" in message

    def test_the_message_names_what_cmecf_actually_served(self) -> None:
        """So the user can see the diagnosis, not just be told it."""
        with pytest.raises(NotAnEFilerError) as e:
            _court().check_filing_entitlement(FakePage(READ_ONLY_MENU))
        message = str(e.value)
        for item in READ_ONLY_MENU:
            assert item in message
        assert "Civil or Criminal" in message

    def test_the_message_says_nothing_was_filed(self) -> None:
        with pytest.raises(NotAnEFilerError) as e:
            _court().check_filing_entitlement(FakePage(READ_ONLY_MENU))
        assert "Nothing was filed" in str(e.value)

    def test_the_message_points_at_the_next_human_step(self) -> None:
        with pytest.raises(NotAnEFilerError) as e:
            _court().check_filing_entitlement(FakePage(READ_ONLY_MENU))
        message = str(e.value)
        assert "Manage My Account" in message
        assert "nef-roundtrip-runbook.md" in message

    def test_it_does_not_blame_a_selector(self) -> None:
        with pytest.raises(NotAnEFilerError) as e:
            _court().check_filing_entitlement(FakePage(READ_ONLY_MENU))
        assert "#event_list" not in str(e.value)


class TestFilerAccountsPass:
    def test_a_filing_menu_is_enough(self) -> None:
        _court().check_filing_entitlement(FakePage(FILER_MENU))

    def test_criminal_only_account_may_still_file(self) -> None:
        _court().check_filing_entitlement(
            FakePage(["Criminal", "Query", "Reports", "Log Out"])
        )

    def test_case_and_spacing_do_not_matter(self) -> None:
        _court().check_filing_entitlement(
            FakePage(["  civil  ", "Query", "Log Out"])
        )

    def test_no_menu_bar_at_all_is_not_a_permissions_answer(self) -> None:
        """An error page or a redirect must not be reported as "not a filer"."""
        _court().check_filing_entitlement(FakePage(["Home", "Contact us"]))

    def test_empty_page_passes_through(self) -> None:
        _court().check_filing_entitlement(FakePage([]))

    def test_detached_nodes_are_skipped_not_fatal(self) -> None:
        page = FakePage([DetachedAnchor("Civil"), "Query", "Log Out"])
        with pytest.raises(NotAnEFilerError):
            _court().check_filing_entitlement(page)


class TestSubstringMatchesDoNotCount:
    """A docket page is full of links containing the word "civil"."""

    def test_civil_cover_sheet_link_is_not_a_filing_menu(self) -> None:
        with pytest.raises(NotAnEFilerError):
            _court().check_filing_entitlement(
                FakePage(
                    ["Civil Cover Sheet JS-44", "Query", "Reports", "Log Out"]
                )
            )

    def test_civil_case_docket_link_is_not_a_filing_menu(self) -> None:
        with pytest.raises(NotAnEFilerError):
            _court().check_filing_entitlement(
                FakePage(["View Civil Docket", "Query", "Utilities", "Log Out"])
            )


class TestPerCourtTypeMenus:
    def _profile(self, court_type: str) -> CourtProfile:
        return CourtProfile(
            court_id="x",
            name="X",
            court_type=court_type,
            ecf_url="https://ecf.example.uscourts.gov",
        )

    def test_bankruptcy_wants_its_own_menus(self) -> None:
        court = BankruptcyCourt(self._profile("bankruptcy"))
        court.check_filing_entitlement(FakePage(["Bankruptcy", "Query"]))
        with pytest.raises(NotAnEFilerError) as e:
            court.check_filing_entitlement(FakePage(READ_ONLY_MENU))
        assert "Bankruptcy or Adversary" in str(e.value)

    def test_a_civil_menu_does_not_entitle_a_bankruptcy_filing(self) -> None:
        court = BankruptcyCourt(self._profile("bankruptcy"))
        with pytest.raises(NotAnEFilerError):
            court.check_filing_entitlement(FakePage(["Civil", "Query", "Log Out"]))

    def test_appellate_skips_the_check(self) -> None:
        """TransportRoom is not the district menu bar — no false negatives."""
        AppellateCourt(self._profile("appellate")).check_filing_entitlement(
            FakePage(READ_ONLY_MENU)
        )


class TestItIsNotRetried:
    """Three attempts at a permissions failure is three times the confusion."""

    def test_retry_on_error_gives_up_immediately(self) -> None:
        calls = []

        def action() -> None:
            calls.append(1)
            raise NotAnEFilerError("not a filer")

        with pytest.raises(NotAnEFilerError):
            retry_on_error(action, description="select event")
        assert len(calls) == 1

    def test_ordinary_form_errors_are_still_retried(self) -> None:
        from ecfiler.courts.base import ECFFormError

        calls = []

        def action() -> None:
            calls.append(1)
            raise ECFFormError("transient")

        with pytest.raises(ECFFormError):
            retry_on_error(action, delay=0, description="select event")
        assert len(calls) == 3


class TestSelectEventExplainsItself:
    def test_missing_event_list_checks_entitlement_first(self) -> None:
        """The event list was missing *because* of permissions — say that."""

        class NoEventListPage(FakePage):
            def query_selector(self, selector: str):
                return None

        court = _court()
        with pytest.raises(NotAnEFilerError):
            court.select_event(NoEventListPage(READ_ONLY_MENU), "16")

    def test_a_filer_gets_the_page_it_was_reading(self) -> None:
        from ecfiler.courts.base import ECFFormError

        class NoEventListPage(FakePage):
            def query_selector(self, selector: str):
                return None

        court = _court()
        page = NoEventListPage(FILER_MENU, url="https://ecf.tc1d.aztc.uscourts.gov/cgi-bin/iquery.pl")
        with pytest.raises(ECFFormError) as e:
            court.select_event(page, "16")
        assert "iquery.pl" in str(e.value)


class TestFilingUrlIsNotTheQueryUrl:
    """`ecf_filing_url` in a staged package pointed at the query CGI."""

    def test_query_url_is_iquery(self) -> None:
        assert _court().profile.query_url.endswith("/cgi-bin/iquery.pl")

    def test_filing_url_is_no_longer_the_query_cgi(self) -> None:
        assert "iquery.pl" not in _court().profile.filing_url

    def test_staged_packages_do_not_send_filers_to_the_query_screen(self) -> None:
        from ecfiler.courts.registry import CourtRegistry

        profile = CourtRegistry(environment="qa").get("azttdc").profile
        assert "iquery.pl" not in profile.filing_url
