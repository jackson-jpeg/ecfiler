"""Tests for certificate of service generation."""

from datetime import date
from pathlib import Path

import pytest

from ecfiler.agent.certificate_of_service import (
    CertificateOfService,
    ServiceRecipient,
    generate_certificate,
    generate_certificate_pdf,
)


@pytest.fixture
def ecf_recipients() -> list[ServiceRecipient]:
    return [
        ServiceRecipient(
            name="Jones Corp",
            role="defendant",
            attorney_name="John Adams",
            attorney_firm="Adams & Associates",
            method="CM/ECF",
        ),
        ServiceRecipient(
            name="Doe LLC",
            role="defendant",
            attorney_name="Bob Carter",
            attorney_firm="Carter Law",
            method="CM/ECF",
        ),
    ]


@pytest.fixture
def mixed_recipients() -> list[ServiceRecipient]:
    return [
        ServiceRecipient(
            name="Jones Corp",
            role="defendant",
            attorney_name="John Adams",
            method="CM/ECF",
        ),
        ServiceRecipient(
            name="Pro Se Litigant",
            role="defendant",
            method="mail",
            address="123 Main St, New York, NY 10001",
        ),
    ]


class TestGenerateCertificate:
    def test_all_ecf(self, ecf_recipients: list[ServiceRecipient]) -> None:
        cert = generate_certificate(
            recipients=ecf_recipients,
            attorney_name="Jane Smith",
            filing_date=date(2024, 12, 15),
        )
        assert cert.is_all_ecf
        assert "December 15, 2024" in cert.text
        assert "Jane Smith" in cert.text
        assert "CM/ECF" in cert.text
        assert "electronically filed" in cert.text
        assert "/s/ Jane Smith" in cert.text

    def test_mixed_methods(self, mixed_recipients: list[ServiceRecipient]) -> None:
        cert = generate_certificate(
            recipients=mixed_recipients,
            attorney_name="Jane Smith",
        )
        assert not cert.is_all_ecf
        assert cert.method == "mixed"
        assert "John Adams" in cert.text
        assert "first-class U.S. mail" in cert.text
        assert "123 Main St" in cert.text

    def test_default_date_is_today(self, ecf_recipients: list[ServiceRecipient]) -> None:
        cert = generate_certificate(
            recipients=ecf_recipients,
            attorney_name="Jane Smith",
        )
        today = date.today().strftime("%B")
        assert today in cert.filing_date

    def test_single_recipient(self) -> None:
        cert = generate_certificate(
            recipients=[
                ServiceRecipient(
                    name="Defendant",
                    role="defendant",
                    attorney_name="Opposing Counsel",
                    method="CM/ECF",
                )
            ],
            attorney_name="Filing Attorney",
        )
        assert cert.is_all_ecf
        assert "Filing Attorney" in cert.text

    def test_email_service(self) -> None:
        cert = generate_certificate(
            recipients=[
                ServiceRecipient(
                    name="Party",
                    role="defendant",
                    method="email",
                    email="party@example.com",
                ),
            ],
            attorney_name="Attorney",
        )
        assert not cert.is_all_ecf
        assert "party@example.com" in cert.text


class TestGeneratePdf:
    def test_creates_pdf(self, ecf_recipients: list[ServiceRecipient], tmp_path: Path) -> None:
        cert = generate_certificate(
            recipients=ecf_recipients,
            attorney_name="Jane Smith",
        )
        output = str(tmp_path / "cos.pdf")
        result = generate_certificate_pdf(
            cert, output, case_number="1:24-cv-01234", court_name="S.D.N.Y."
        )
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0

    def test_pdf_is_valid(self, ecf_recipients: list[ServiceRecipient], tmp_path: Path) -> None:
        cert = generate_certificate(
            recipients=ecf_recipients,
            attorney_name="Jane Smith",
        )
        output = str(tmp_path / "cos.pdf")
        generate_certificate_pdf(cert, output)

        # Validate with our own validator
        from ecfiler.pdf.validator import validate_pdf
        result = validate_pdf(output)
        assert result.valid
        assert result.has_text
