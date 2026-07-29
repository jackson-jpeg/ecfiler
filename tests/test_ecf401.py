"""ECF 4.01 core message layer — Florida gap item #4.

All fixtures are generated in-test. Illegal states must raise
(ECF401Error), never warn: new-case and fee-bearing paths are outside the
first-application certification scope, and a malformed message that only
warns is how a stranded filing happens.
"""

from __future__ import annotations

import base64
from xml.etree import ElementTree as ET

import pytest

from ecfiler.courts.florida.ecf401 import (
    FL_EXTENSION_NS,
    NS,
    Attachment,
    ECF401Error,
    MessageReceipt,
    ReviewFilingRequest,
    build_review_filing,
    parse_message_receipt,
    parse_review_complete,
)
from ecfiler.courts.florida.submission import SubmissionStatus

UCN = "292026CA000500A001BR"  # Circuit Civil, county 29 — matches test_florida_domain


def _pdf(size: int = 64) -> bytes:
    return b"%PDF-1.7\n" + b"x" * size


def _request(**overrides) -> ReviewFilingRequest:
    defaults = dict(
        ucn=UCN,
        lead_document=Attachment("motion_to_compel.pdf", _pdf(), "Motion"),
        connected_documents=[Attachment("exhibit_a.pdf", _pdf(32), "Exhibit")],
        filing_code="MOTION",
        filing_description="Motion to Compel Discovery",
        submitter_name="Jane Doe, Esq.",
    )
    defaults.update(overrides)
    return ReviewFilingRequest(**defaults)


class TestRequestInvariants:
    def test_valid_request_builds(self) -> None:
        assert _request()

    def test_invalid_ucn_raises(self) -> None:
        with pytest.raises(ECF401Error, match="invalid UCN"):
            _request(ucn="NOT-A-UCN")

    def test_fee_bearing_raises(self) -> None:
        with pytest.raises(ECF401Error, match="fee-bearing"):
            _request(fee_amount=10.0)

    def test_missing_submitter_raises(self) -> None:
        with pytest.raises(ECF401Error, match="submitter_name"):
            _request(submitter_name="  ")

    def test_empty_attachment_raises(self) -> None:
        with pytest.raises(ECF401Error, match="empty"):
            Attachment("motion.pdf", b"")

    def test_illegal_filename_raises(self) -> None:
        with pytest.raises(ECF401Error, match="violates Portal rules"):
            Attachment("mo*tion?.pdf", _pdf())

    def test_over_50mb_submission_raises(self) -> None:
        with pytest.raises(ECF401Error, match="50 MB"):
            _request(
                lead_document=Attachment("big.pdf", _pdf(51 * 1024 * 1024)),
                connected_documents=[],
            )


class TestBuildReviewFiling:
    def test_produces_namespaced_core_filing_message(self) -> None:
        xml = build_review_filing(_request())
        root = ET.fromstring(xml)
        assert root.tag == f"{{{NS['core']}}}CoreFilingMessage"

    def test_case_tracking_id_is_the_ucn(self) -> None:
        root = ET.fromstring(build_review_filing(_request()))
        tracking = root.find(f".//{{{NS['nc']}}}CaseTrackingID")
        assert tracking is not None and tracking.text == UCN

    def test_county_code_isolated_in_extension_namespace(self) -> None:
        root = ET.fromstring(build_review_filing(_request()))
        county = root.find(f".//{{{FL_EXTENSION_NS}}}CountyCode")
        assert county is not None and county.text == "29"

    def test_exactly_one_lead_document(self) -> None:
        root = ET.fromstring(build_review_filing(_request()))
        leads = root.findall(f"{{{NS['core']}}}FilingLeadDocument")
        connected = root.findall(f"{{{NS['core']}}}FilingConnectedDocument")
        assert len(leads) == 1
        assert len(connected) == 1

    def test_attachment_round_trips_through_base64(self) -> None:
        content = _pdf(128)
        request = _request(lead_document=Attachment("motion.pdf", content))
        root = ET.fromstring(build_review_filing(request))
        lead = root.find(f"{{{NS['core']}}}FilingLeadDocument")
        binary = lead.find(f".//{{{NS['nc']}}}BinaryBase64Object")
        assert base64.b64decode(binary.text) == content

    def test_submitter_name_present(self) -> None:
        root = ET.fromstring(build_review_filing(_request()))
        full = root.find(f".//{{{NS['nc']}}}PersonFullName")
        assert full is not None and full.text == "Jane Doe, Esq."


def _receipt_xml(errors: list[tuple[str, str]], submission_id: str = "SUB-123") -> bytes:
    ns_r, ns_e, ns_nc = NS["receipt"], NS["ecf"], NS["nc"]
    error_xml = "".join(
        f'<ecf:Error><ecf:ErrorCode>{code}</ecf:ErrorCode>'
        f"<ecf:ErrorText>{text}</ecf:ErrorText></ecf:Error>"
        for code, text in errors
    )
    return (
        f'<receipt:MessageReceiptMessage xmlns:receipt="{ns_r}" '
        f'xmlns:ecf="{ns_e}" xmlns:nc="{ns_nc}">'
        f"<nc:DocumentIdentification><nc:IdentificationID>{submission_id}"
        f"</nc:IdentificationID></nc:DocumentIdentification>"
        f"{error_xml}</receipt:MessageReceiptMessage>"
    ).encode()


class TestParseMessageReceipt:
    def test_success_receipt(self) -> None:
        receipt = parse_message_receipt(_receipt_xml([("0", "No error")]))
        assert receipt == MessageReceipt(accepted=True, submission_id="SUB-123", errors=[])

    def test_error_receipt(self) -> None:
        receipt = parse_message_receipt(
            _receipt_xml([("72", "Filing size exceeds maximum")])
        )
        assert receipt.accepted is False
        assert receipt.errors == [("72", "Filing size exceeds maximum")]

    def test_garbage_raises(self) -> None:
        with pytest.raises(ECF401Error, match="not well-formed"):
            parse_message_receipt(b"<not xml")

    def test_wrong_root_raises(self) -> None:
        with pytest.raises(ECF401Error, match="expected MessageReceiptMessage"):
            parse_message_receipt(b"<SomethingElse/>")


def _review_xml(status: str, comment: str = "", submission_id: str = "SUB-123") -> bytes:
    ns_v, ns_e, ns_nc = NS["review"], NS["ecf"], NS["nc"]
    comment_xml = (
        f"<ecf:FilingReviewCommentsText>{comment}</ecf:FilingReviewCommentsText>"
        if comment
        else ""
    )
    status_xml = f"<ecf:FilingStatus>{status}</ecf:FilingStatus>" if status else ""
    return (
        f'<review:FilingReviewCompleteNotificationMessage xmlns:review="{ns_v}" '
        f'xmlns:ecf="{ns_e}" xmlns:nc="{ns_nc}">'
        f"<nc:DocumentIdentification><nc:IdentificationID>{submission_id}"
        f"</nc:IdentificationID></nc:DocumentIdentification>"
        f"{status_xml}{comment_xml}"
        f"</review:FilingReviewCompleteNotificationMessage>"
    ).encode()


class TestParseReviewComplete:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("Accepted", SubmissionStatus.ACCEPTED),
            ("Docketed", SubmissionStatus.ACCEPTED),
            ("Correction Queue", SubmissionStatus.CORRECTION_QUEUE),
            ("Abandoned", SubmissionStatus.ABANDONED),
            ("Under Review", SubmissionStatus.UNDER_REVIEW),
            ("Received", SubmissionStatus.RECEIVED),
        ],
    )
    def test_status_maps_to_submission_lifecycle(self, raw, expected) -> None:
        result = parse_review_complete(_review_xml(raw))
        assert result.status is expected
        assert result.raw_status == raw
        assert result.submission_id == "SUB-123"

    def test_reviewer_comment_captured(self) -> None:
        result = parse_review_complete(
            _review_xml("Correction Queue", comment="Wrong division selected")
        )
        assert result.reviewer_comment == "Wrong division selected"

    def test_unknown_status_raises_rather_than_guessing(self) -> None:
        with pytest.raises(ECF401Error, match="unknown review status"):
            parse_review_complete(_review_xml("Frobnicated"))

    def test_missing_status_raises(self) -> None:
        with pytest.raises(ECF401Error, match="no FilingStatus"):
            parse_review_complete(_review_xml(""))


class TestRoundTrip:
    def test_build_then_reparse_preserves_every_document(self) -> None:
        request = _request(
            connected_documents=[
                Attachment("exhibit_a.pdf", _pdf(16)),
                Attachment("exhibit_b.pdf", _pdf(24)),
            ]
        )
        root = ET.fromstring(build_review_filing(request))
        filenames = [
            el.text
            for el in root.iter(f"{{{NS['nc']}}}DocumentFileControlID")
        ]
        assert filenames == ["motion_to_compel.pdf", "exhibit_a.pdf", "exhibit_b.pdf"]
