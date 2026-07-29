"""The "5-point readiness check" named in public copy is exactly this gate.

The pricing tiers (web/lib/facts.ts), Terms §5, and the landing page all
describe a five-check readiness gate before a filing can be staged. This
test pins the count and the components to ecfiler.api.streaming so the
copy stays a claim about code, not copywriting.
"""

from ecfiler.api.streaming import readiness_checks


def _all_green() -> dict[str, bool]:
    return readiness_checks(
        pdf_valid=True,
        redaction_clean=True,
        case_number="1:24-cv-01234",
        event_code="12",
        has_signature=True,
    )


class TestReadinessChecks:
    def test_exactly_five_checks(self) -> None:
        assert len(_all_green()) == 5

    def test_the_five_named_components(self) -> None:
        assert set(_all_green()) == {
            "pdf_valid",
            "redaction_clean",
            "case_number_found",
            "event_code_matched",
            "signature_block_found",
        }

    def test_all_pass_when_everything_present(self) -> None:
        assert all(_all_green().values())

    def test_missing_case_number_fails_its_check(self) -> None:
        checks = readiness_checks(
            pdf_valid=True,
            redaction_clean=True,
            case_number=None,
            event_code="12",
            has_signature=True,
        )
        assert checks["case_number_found"] is False
        assert sum(checks.values()) == 4

    def test_empty_event_code_fails_its_check(self) -> None:
        checks = readiness_checks(
            pdf_valid=True,
            redaction_clean=True,
            case_number="1:24-cv-01234",
            event_code="",
            has_signature=False,
        )
        assert checks["event_code_matched"] is False
        assert checks["signature_block_found"] is False
        assert sum(checks.values()) == 3
