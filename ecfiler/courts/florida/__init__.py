"""Florida Courts E-Filing Portal domain model.

Pre-approval work only. The wire protocol (ECF 4.01 plus Florida's proprietary
Portal extensions) is not modelled here because its XSDs are released only after
the Third Party Vendor application is approved — see
`docs/fl-certification-gap-analysis.md`. What lives here is what the public
program documents fully determine: the Uniform Case Number, and the submission
lifecycle the TS001–TS009 test scenarios exercise.
"""

from ecfiler.courts.florida.submission import (
    CORRECTION_WINDOW_BUSINESS_DAYS,
    TEST_COUNTY_MATRIX,
    Document,
    FilingPath,
    Submission,
    SubmissionStateError,
    SubmissionStatus,
    add_business_days,
    certification_submission_count,
    new_existing_case_submission,
)
from ecfiler.courts.florida.ucn import (
    COUNTY_CODES,
    COURT_TYPES,
    FIRST_CERTIFICATION_COURT_TYPES,
    UCN,
    UCNError,
    county_code_for,
    is_valid_ucn,
    parse_ucn,
)

__all__ = [
    "CORRECTION_WINDOW_BUSINESS_DAYS",
    "COUNTY_CODES",
    "COURT_TYPES",
    "FIRST_CERTIFICATION_COURT_TYPES",
    "TEST_COUNTY_MATRIX",
    "Document",
    "FilingPath",
    "Submission",
    "SubmissionStateError",
    "SubmissionStatus",
    "UCN",
    "UCNError",
    "add_business_days",
    "certification_submission_count",
    "county_code_for",
    "is_valid_ucn",
    "new_existing_case_submission",
    "parse_ucn",
]
