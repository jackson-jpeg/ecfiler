"""Florida Courts E-Filing Portal domain model.

Pre-approval work only. What lives here is what the public program documents
fully determine: the Uniform Case Number, the submission lifecycle the
TS001–TS009 test scenarios exercise, the Technology Standards §2 document
rules, and — in `ecf401.py` — a ReviewFiling construction / response-parsing
skeleton against the public OASIS ECF 4.01 spec. Florida's proprietary
Portal-extension XSDs are released only after the Third Party Vendor
application is approved, so everything Florida-wire-specific in ecf401 is
isolated behind one placeholder namespace and priced as rework — see
`docs/fl-certification-gap-analysis.md` §6.
"""

from ecfiler.courts.florida.document_rules import (
    APPELLATE_SUBMISSION_LIMIT_MB,
    FORBIDDEN_FILENAME_CHARS,
    MAX_FILENAME_BYTES,
    TRIAL_SUBMISSION_LIMIT_MB,
    DocumentScanResult,
    FloridaDocumentError,
    ProhibitedFinding,
    prepare_document_for_portal,
    scan_prohibited_elements,
    scrub_prohibited_elements,
    validate_filename,
    validate_submission_files,
)
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
    "APPELLATE_SUBMISSION_LIMIT_MB",
    "CORRECTION_WINDOW_BUSINESS_DAYS",
    "COUNTY_CODES",
    "COURT_TYPES",
    "FIRST_CERTIFICATION_COURT_TYPES",
    "FORBIDDEN_FILENAME_CHARS",
    "MAX_FILENAME_BYTES",
    "TEST_COUNTY_MATRIX",
    "TRIAL_SUBMISSION_LIMIT_MB",
    "Document",
    "DocumentScanResult",
    "FilingPath",
    "FloridaDocumentError",
    "ProhibitedFinding",
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
    "prepare_document_for_portal",
    "scan_prohibited_elements",
    "scrub_prohibited_elements",
    "validate_filename",
    "validate_submission_files",
]
