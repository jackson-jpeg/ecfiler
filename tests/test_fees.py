"""Tests for the filing fee schedule."""

from ecfiler.filing.fees import FilingFee, format_fee, get_fee


class TestDistrictFees:
    def test_complaint(self) -> None:
        fee = get_fee("Complaint", "district")
        assert fee is not None
        assert fee.amount == 405.00

    def test_motion_no_fee(self) -> None:
        fee = get_fee("Motion to Dismiss", "district")
        assert fee is not None
        assert fee.amount == 0
        assert fee.waivable is True

    def test_removal(self) -> None:
        fee = get_fee("Notice of Removal", "district")
        assert fee is not None
        assert fee.amount == 405.00

    def test_answer_no_fee(self) -> None:
        fee = get_fee("Answer", "district")
        assert fee is not None
        assert fee.amount == 0


class TestBankruptcyFees:
    def test_chapter7(self) -> None:
        fee = get_fee("Chapter 7 Voluntary Petition", "bankruptcy")
        assert fee is not None
        assert fee.amount == 338.00

    def test_chapter11(self) -> None:
        fee = get_fee("Chapter 11 Petition", "bankruptcy")
        assert fee is not None
        assert fee.amount == 1738.00

    def test_chapter11_sub5(self) -> None:
        fee = get_fee("Chapter 11 Subchapter V Petition", "bankruptcy")
        assert fee is not None
        assert fee.amount == 1738.00

    def test_chapter13(self) -> None:
        fee = get_fee("Chapter 13 Petition", "bankruptcy")
        assert fee is not None
        assert fee.amount == 313.00

    def test_adversary(self) -> None:
        fee = get_fee("Adversary Complaint", "bankruptcy")
        assert fee is not None
        assert fee.amount == 350.00


class TestAppellateFees:
    def test_notice_of_appeal(self) -> None:
        fee = get_fee("Notice of Appeal", "appellate")
        assert fee is not None
        assert fee.amount == 505.00

    def test_rehearing_no_fee(self) -> None:
        fee = get_fee("Petition for Rehearing", "appellate")
        assert fee is not None
        assert fee.amount == 0


class TestUnknown:
    def test_unknown_event_returns_none(self) -> None:
        assert get_fee("frobnicate the widget", "district") is None

    def test_empty_returns_none(self) -> None:
        assert get_fee("", "district") is None


class TestFormatFee:
    def test_format_paid_fee(self) -> None:
        text = format_fee(FilingFee(405.00, "Civil action filing fee"))
        assert "$405.00" in text
        assert "Civil action filing fee" in text

    def test_format_zero_fee(self) -> None:
        assert format_fee(FilingFee(0, "No fee")) == "No filing fee"
