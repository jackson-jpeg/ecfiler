"""Tests for the Florida pre-approval domain model.

Fixtures are drawn from the primary sources rather than invented: the 1998
Supreme Court order's example UCN (012000CF000001A000XX) and the Tech Memo
2023-01 examples of forbidden filler values.
"""

from __future__ import annotations

from datetime import date, datetime

import pytest

from ecfiler.courts.florida import (
    COUNTY_CODES,
    COURT_TYPES,
    TEST_COUNTY_MATRIX,
    Document,
    FilingPath,
    Submission,
    SubmissionStateError,
    SubmissionStatus,
    UCNError,
    add_business_days,
    certification_submission_count,
    county_code_for,
    is_valid_ucn,
    new_existing_case_submission,
    parse_ucn,
)
from ecfiler.courts.florida.ucn import validate_party_identifier_variation3

# From the 1998 order, Appendix: "Sample: 012000CF000001A000XX"
ORDER_EXAMPLE = "012000CF000001A000XX"
# A Circuit Civil case in Hillsborough (Tampa), the first-certification scope.
CIRCUIT_CIVIL = "292026CA000500A001BR"


class TestUCNParsing:
    def test_parses_the_supreme_court_orders_own_example(self):
        # strict=False: the 1998 order's own sample ends in branch 'XX', which
        # the 2023 memo later forbade as a filler value. The memo expressly does
        # not require existing UCNs to be corrected, so a UCN that predates it
        # must still parse — it just fails state-reporting validation.
        ucn = parse_ucn(ORDER_EXAMPLE, strict=False)
        assert is_valid_ucn(ORDER_EXAMPLE) is False
        assert ucn.county_code == "01"
        assert ucn.county_name == "Alachua"
        assert ucn.year == "2000"
        assert ucn.court_type == "CF"
        assert ucn.court_type_name == "Felony"
        assert ucn.sequential_number == "000001"
        assert ucn.party_identifier == "A000"
        assert ucn.branch_location == "XX"

    def test_roundtrips_to_canonical_string(self):
        assert str(parse_ucn(CIRCUIT_CIVIL)) == CIRCUIT_CIVIL

    def test_tolerates_display_formatting_on_input(self):
        spaced = "29 2026 CA 000500 A001 BR"
        hyphenated = "29-2026-CA-000500-A001-BR"
        assert str(parse_ucn(spaced)) == CIRCUIT_CIVIL
        assert str(parse_ucn(hyphenated)) == CIRCUIT_CIVIL

    def test_lowercase_is_normalized(self):
        assert str(parse_ucn(CIRCUIT_CIVIL.lower())) == CIRCUIT_CIVIL

    @pytest.mark.parametrize("bad", ["", "292026CA000500A001", "292026CA000500A001BRX"])
    def test_wrong_length_rejected(self, bad):
        with pytest.raises(UCNError, match="20 characters"):
            parse_ucn(bad)

    def test_none_rejected(self):
        with pytest.raises(UCNError):
            parse_ucn(None)

    def test_non_alphanumeric_rejected(self):
        with pytest.raises(UCNError, match="alphanumeric"):
            parse_ucn("292026CA000500A001B!")

    def test_is_valid_never_raises(self):
        assert is_valid_ucn(CIRCUIT_CIVIL) is True
        assert is_valid_ucn("nonsense") is False
        assert is_valid_ucn(None) is False


class TestUCN14CaseIdentity:
    """UCN14 is the case; party and branch sub-fields do not change identity."""

    def test_ucn14_is_first_fourteen_characters(self):
        assert parse_ucn(CIRCUIT_CIVIL).ucn14 == "292026CA000500"

    def test_same_case_across_different_parties_and_branches(self):
        a = parse_ucn("292026CA000500A001BR")
        b = parse_ucn("292026CA000500B002DT")
        assert a.ucn14 == b.ucn14
        assert str(a) != str(b)

    def test_different_sequence_is_a_different_case(self):
        a = parse_ucn("292026CA000500A001BR")
        b = parse_ucn("292026CA000501A001BR")
        assert a.ucn14 != b.ucn14


class TestStateReportingConstraints:
    """Tech Memo 2023-01 forbids filler sub-fields for state reporting."""

    @pytest.mark.parametrize("party", ["XXXX", "0000"])
    def test_filler_party_identifier_rejected(self, party):
        with pytest.raises(UCNError, match="filler"):
            parse_ucn(f"292026CA000500{party}BR")

    @pytest.mark.parametrize("tail", ["XX", "00"])
    def test_variation3_filler_tail_rejected_when_caller_knows_variation(self, tail):
        # Not enforced at parse time: the variation leaves no trace in the
        # string, and 'AXXX' is valid under variation 1. A caller who knows the
        # county uses variation 3 opts in.
        assert is_valid_ucn(f"292026CA000500WP{tail}BR") is True
        with pytest.raises(UCNError, match="variation 3"):
            validate_party_identifier_variation3(f"WP{tail}")

    def test_variation3_valid_tail_accepted(self):
        validate_party_identifier_variation3("QZAX")
        validate_party_identifier_variation3("WPXA")

    @pytest.mark.parametrize("branch", ["XX", "00"])
    def test_filler_branch_rejected(self, branch):
        with pytest.raises(UCNError, match="filler"):
            parse_ucn(f"292026CA000500A001{branch}")

    def test_osca_reserved_party_id_rejected(self):
        with pytest.raises(UCNError, match="reserved by OSCA"):
            parse_ucn("292026CA000500XXGEBR")

    def test_valid_party_ids_from_the_memo_accepted(self):
        # "party/defendant identifiers 'AXXX', 'XXXG', '0003', 'A00X', or
        # 'BBBB' are valid" — Tech Memo 2023-01.
        for party in ("AXXX", "XXXG", "0003", "A00X", "BBBB"):
            assert is_valid_ucn(f"292026CA000500{party}BR"), party

    def test_variation3_valid_examples_from_the_memo_accepted(self):
        # "'WPXA' and '1G03' are appropriate"; "'QZAX' would be valid".
        for party in ("WPXA", "1G03", "QZAX"):
            assert is_valid_ucn(f"292026CA000500{party}BR"), party

    def test_memo_counterexample_rejected_only_under_variation3(self):
        # "'QZXX' would not be valid since the party/defendant identifier
        # sub-field in variation 3 would be 'XX'" — but only under variation 3,
        # which the string cannot reveal. Parsing accepts it; the explicit
        # variation-3 check is what rejects it.
        assert is_valid_ucn("292026CA000500QZXXBR") is True
        with pytest.raises(UCNError, match="variation 3"):
            validate_party_identifier_variation3("QZXX")

    def test_unknown_county_rejected(self):
        with pytest.raises(UCNError, match="county"):
            parse_ucn("992026CA000500A001BR")

    def test_unknown_court_type_rejected(self):
        with pytest.raises(UCNError, match="court type"):
            parse_ucn("292026ZZ000500A001BR")

    def test_zero_sequence_rejected(self):
        with pytest.raises(UCNError, match="000001"):
            parse_ucn("292026CA000000A001BR")

    def test_legacy_ucn_parses_when_not_strict(self):
        # The memo does not require pre-2024 UCNs to be corrected, so we must
        # still be able to read them.
        legacy = "012000CF000001XXXXXX"
        assert is_valid_ucn(legacy) is False
        ucn = parse_ucn(legacy, strict=False)
        assert ucn.ucn14 == "012000CF000001"


class TestTrafficVariation:
    """TR/CT may substitute a 7-char citation, consuming pos 9-15."""

    def test_citation_number_in_sequence_field_accepted(self):
        ucn = parse_ucn("292026CT" + "A1B2C3D" + "001" + "BR")
        assert ucn.court_type == "CT"
        assert ucn.ucn14 == "292026CTA1B2C3"

    def test_non_traffic_type_must_have_numeric_sequence(self):
        with pytest.raises(UCNError, match="six digits"):
            parse_ucn("292026CA" + "A1B2C3" + "A001" + "BR")


class TestCountyRegistry:
    def test_all_sixty_seven_counties_present(self):
        assert len(COUNTY_CODES) == 67

    def test_lookup_by_name_is_case_insensitive(self):
        assert county_code_for("Hillsborough") == "29"
        assert county_code_for("hillsborough") == "29"

    def test_dade_maps_to_miami_dade(self):
        assert COUNTY_CODES["13"] == "Miami-Dade"
        assert county_code_for("Dade") == "13"
        assert county_code_for("Miami-Dade") == "13"

    def test_unknown_county_returns_none(self):
        assert county_code_for("Atlantis") is None

    def test_first_certification_court_types_are_known(self):
        assert COURT_TYPES["CA"] == "Circuit Civil"
        assert COURT_TYPES["CC"] == "County Civil"

    def test_every_test_matrix_county_resolves(self):
        for slot in TEST_COUNTY_MATRIX:
            for name in slot:
                assert county_code_for(name) is not None, name


class TestSubmissionStructure:
    def _docs(self):
        return [
            Document(filename="motion.pdf", is_lead=True),
            Document(filename="exhibit-a.pdf", is_lead=False),
        ]

    def test_existing_case_requires_ucn(self):
        with pytest.raises(ValueError, match="require a UCN"):
            Submission(ucn=None, filing_path=FilingPath.EXISTING_CASE)

    def test_new_case_must_not_carry_ucn(self):
        with pytest.raises(ValueError, match="must not carry a UCN"):
            Submission(ucn=parse_ucn(CIRCUIT_CIVIL), filing_path=FilingPath.NEW_CASE)

    def test_lead_and_exhibit_split(self):
        s = new_existing_case_submission(CIRCUIT_CIVIL, self._docs())
        assert [d.filename for d in s.lead_documents] == ["motion.pdf"]
        assert [d.filename for d in s.exhibits] == ["exhibit-a.pdf"]

    def test_exhibits_alone_rejected(self):
        s = Submission(
            ucn=parse_ucn(CIRCUIT_CIVIL),
            filing_path=FilingPath.EXISTING_CASE,
            documents=[Document(filename="exhibit.pdf", is_lead=False)],
        )
        with pytest.raises(ValueError, match="no lead document"):
            s.validate_documents()

    def test_empty_submission_rejected(self):
        s = Submission(ucn=parse_ucn(CIRCUIT_CIVIL), filing_path=FilingPath.EXISTING_CASE)
        with pytest.raises(ValueError, match="no documents"):
            s.validate_documents()

    def test_blank_filename_rejected(self):
        with pytest.raises(ValueError, match="filename"):
            Document(filename="   ", is_lead=True)


class TestSubmissionLifecycle:
    def _submission(self):
        return new_existing_case_submission(
            CIRCUIT_CIVIL, [Document(filename="motion.pdf", is_lead=True)]
        )

    def test_happy_path_to_accepted(self):
        s = self._submission()
        s.transition(SubmissionStatus.SUBMITTED)
        s.transition(SubmissionStatus.RECEIVED)
        s.transition(SubmissionStatus.UNDER_REVIEW)
        s.transition(SubmissionStatus.ACCEPTED)
        assert s.status.is_terminal

    def test_correction_and_resubmission_cycle(self):
        s = self._submission()
        s.transition(SubmissionStatus.SUBMITTED)
        s.transition(SubmissionStatus.RECEIVED)
        s.transition(SubmissionStatus.CORRECTION_QUEUE, "missing signature")
        assert s.status.needs_filer_action
        s.transition(SubmissionStatus.RESUBMITTED)
        s.transition(SubmissionStatus.RECEIVED)
        s.transition(SubmissionStatus.ACCEPTED)
        assert s.status is SubmissionStatus.ACCEPTED

    def test_illegal_transition_raises(self):
        s = self._submission()
        with pytest.raises(SubmissionStateError, match="Cannot move from draft"):
            s.transition(SubmissionStatus.ACCEPTED)

    def test_terminal_states_are_final(self):
        s = self._submission()
        s.transition(SubmissionStatus.SUBMITTED)
        s.transition(SubmissionStatus.RECEIVED)
        s.transition(SubmissionStatus.ACCEPTED)
        with pytest.raises(SubmissionStateError, match="terminal"):
            s.transition(SubmissionStatus.CORRECTION_QUEUE)

    def test_abandonment_from_correction_queue(self):
        s = self._submission()
        s.transition(SubmissionStatus.SUBMITTED)
        s.transition(SubmissionStatus.RECEIVED)
        s.transition(SubmissionStatus.CORRECTION_QUEUE)
        s.transition(SubmissionStatus.ABANDONED)
        assert s.status.is_terminal

    def test_history_records_each_step(self):
        s = self._submission()
        s.transition(SubmissionStatus.SUBMITTED, "sent")
        s.transition(SubmissionStatus.RECEIVED, "sub #123")
        assert [n for _, n in s.history] == ["sent", "sub #123"]


class TestCorrectionDeadline:
    def _in_correction(self, when: datetime):
        s = new_existing_case_submission(
            CIRCUIT_CIVIL, [Document(filename="motion.pdf", is_lead=True)]
        )
        s.transition(SubmissionStatus.SUBMITTED, now=when)
        s.transition(SubmissionStatus.RECEIVED, now=when)
        s.transition(SubmissionStatus.CORRECTION_QUEUE, now=when)
        return s

    def test_deadline_is_five_business_days_out(self):
        # Monday 2026-07-27 + 5 business days = Monday 2026-08-03.
        s = self._in_correction(datetime(2026, 7, 27, 9, 0))
        assert s.correction_deadline == date(2026, 8, 3)

    def test_not_past_deadline_before_it(self):
        s = self._in_correction(datetime(2026, 7, 27, 9, 0))
        assert s.is_past_correction_deadline(date(2026, 8, 3)) is False

    def test_past_deadline_after_it(self):
        s = self._in_correction(datetime(2026, 7, 27, 9, 0))
        assert s.is_past_correction_deadline(date(2026, 8, 4)) is True

    def test_resubmission_clears_the_deadline(self):
        s = self._in_correction(datetime(2026, 7, 27, 9, 0))
        s.transition(SubmissionStatus.RESUBMITTED)
        assert s.correction_deadline is None

    def test_deadline_irrelevant_outside_correction_queue(self):
        s = new_existing_case_submission(
            CIRCUIT_CIVIL, [Document(filename="motion.pdf", is_lead=True)]
        )
        assert s.is_past_correction_deadline(date(2030, 1, 1)) is False


class TestBusinessDays:
    def test_skips_weekend(self):
        # Friday 2026-07-31 + 1 business day = Monday 2026-08-03.
        assert add_business_days(date(2026, 7, 31), 1) == date(2026, 8, 3)

    def test_zero_days_is_identity(self):
        assert add_business_days(date(2026, 7, 28), 0) == date(2026, 7, 28)

    def test_five_days_from_monday(self):
        assert add_business_days(date(2026, 7, 27), 5) == date(2026, 8, 3)

    def test_negative_rejected(self):
        with pytest.raises(ValueError):
            add_business_days(date(2026, 7, 28), -1)


class TestCertificationVolume:
    def test_eight_county_targets(self):
        assert len(TEST_COUNTY_MATRIX) == 8

    def test_planned_scope_is_sixty_four_submissions(self):
        # 4 scenarios (TS001/TS002/TS005/TS006) x 2 divisions (CA, CC) x 8 counties
        assert certification_submission_count(scenarios=4, divisions=2) == 64

    def test_zero_scope_is_zero(self):
        assert certification_submission_count(scenarios=0, divisions=2) == 0

    def test_negative_rejected(self):
        with pytest.raises(ValueError):
            certification_submission_count(scenarios=-1, divisions=2)
