"""Florida Portal document rules — PDF/A enforcement, prohibited elements,
size and filename limits.

Every rule here traces to the Florida Courts Technology Standards v4.0
(adopted May 2023, revised May 2025), Section 2, as captured verbatim in
docs/fl/technical-specs.md §4:

- "A single submission, whether consisting of a single document or multiple
  documents, shall not exceed 50 megabytes (50 MB) in size." (trial courts;
  appellate limits are higher — 200 MB per the Portal FAQs)
- Prohibited PDF/A elements: "embedded attachments, comments, annotations,
  hidden deleted items (purge them), embedded non-persistent external
  hyperlinks, embedded thumbnails, form fields and actions, JavaScript,
  embedded non-display data."
- Permitted elements include bookmarks, internal links, and persistent
  external hyperlinks — so link annotations are allowed and every other
  annotation subtype is not.
- Encryption: "A compliant PDF/A file must be open and available to anyone or
  any software that processes the file."
- File names (Section 2.1.6): no `"` `#` `%` `&` `*` `:` `<` `>` characters;
  maximum 150 bytes including spaces.

The federal pipeline keeps its own limits (validator default 100 MB); these
rules are Florida-scoped and never applied to federal filings. Illegal states
raise — a submission that violates a hard rule is refused, not warned about,
because the Portal's own remedy is the Correction Queue and a five-business-day
clock (Standards 2.2.5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import pikepdf

from ecfiler.courts.florida.submission import Submission

# Standards §2.1.2; appellate figure from the Portal FAQs.
TRIAL_SUBMISSION_LIMIT_MB = 50
APPELLATE_SUBMISSION_LIMIT_MB = 200

# Standards §2.1.6.
FORBIDDEN_FILENAME_CHARS = frozenset('"#%&*:<>')
MAX_FILENAME_BYTES = 150

# Annotation subtypes that survive a scrub. /Link covers both internal links
# and persistent external hyperlinks, which the Standards expressly permit.
_ALLOWED_ANNOTATION_SUBTYPES = {"/Link"}


class FloridaDocumentError(Exception):
    """A document or submission violates a hard Portal rule."""


@dataclass
class ProhibitedFinding:
    """One prohibited element found in a PDF."""

    element: str  # e.g. "form-fields", "javascript"
    detail: str
    scrubbable: bool = True


@dataclass
class DocumentScanResult:
    path: str
    findings: list[ProhibitedFinding] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return not self.findings


def validate_filename(name: str) -> list[str]:
    """Filename errors under Standards §2.1.6. Empty list means compliant."""
    errors: list[str] = []
    bad = sorted(set(name) & FORBIDDEN_FILENAME_CHARS)
    if bad:
        errors.append(
            f"filename contains forbidden character(s) {' '.join(bad)}: {name!r}"
        )
    byte_len = len(name.encode("utf-8"))
    if byte_len > MAX_FILENAME_BYTES:
        errors.append(
            f"filename is {byte_len} bytes; the Portal caps names at "
            f"{MAX_FILENAME_BYTES} bytes including spaces"
        )
    if not name.strip():
        errors.append("filename is empty")
    return errors


def scan_prohibited_elements(path: str | Path) -> DocumentScanResult:
    """Detect the Standards' prohibited PDF/A elements in a PDF.

    Detection is structural (pikepdf object inspection). "Hidden deleted
    items" from incremental updates are handled by the scrub (a full rewrite
    drops orphaned objects) rather than detected individually.
    """
    p = Path(path)
    result = DocumentScanResult(path=str(p))

    try:
        pdf = pikepdf.open(p)
    except pikepdf.PasswordError:
        result.findings.append(
            ProhibitedFinding(
                element="encryption",
                detail="PDF is password-protected; compliant PDF/A must be "
                "open to anyone processing the file",
                scrubbable=False,
            )
        )
        return result

    with pdf:
        if pdf.is_encrypted:
            result.findings.append(
                ProhibitedFinding(
                    element="encryption",
                    detail="PDF is encrypted; encryption is prohibited",
                    scrubbable=True,  # pikepdf decrypts empty-owner-password files on save
                )
            )

        root = pdf.Root
        if "/AcroForm" in root:
            result.findings.append(
                ProhibitedFinding(
                    element="form-fields",
                    detail="document carries an AcroForm dictionary (form "
                    "fields and actions are prohibited)",
                )
            )
        if "/OpenAction" in root:
            result.findings.append(
                ProhibitedFinding(
                    element="actions",
                    detail="document has an OpenAction (document-level actions "
                    "are prohibited)",
                )
            )
        if "/AA" in root:
            result.findings.append(
                ProhibitedFinding(
                    element="actions",
                    detail="document has additional-actions (/AA)",
                )
            )
        names = root.get("/Names", None)
        if names is not None:
            if "/JavaScript" in names:
                result.findings.append(
                    ProhibitedFinding(
                        element="javascript",
                        detail="document-level JavaScript name tree",
                    )
                )
            if "/EmbeddedFiles" in names:
                result.findings.append(
                    ProhibitedFinding(
                        element="embedded-attachments",
                        detail="embedded file attachments (EmbeddedFiles name tree)",
                    )
                )
        if "/PieceInfo" in root:
            result.findings.append(
                ProhibitedFinding(
                    element="non-display-data",
                    detail="private application data (/PieceInfo) — embedded "
                    "non-display data is prohibited",
                )
            )

        for page_index, page in enumerate(pdf.pages, start=1):
            if "/Thumb" in page:
                result.findings.append(
                    ProhibitedFinding(
                        element="thumbnails",
                        detail=f"page {page_index} carries an embedded thumbnail",
                    )
                )
            if "/AA" in page:
                result.findings.append(
                    ProhibitedFinding(
                        element="actions",
                        detail=f"page {page_index} has page-level actions (/AA)",
                    )
                )
            for annot in page.get("/Annots", []):
                subtype = str(annot.get("/Subtype", ""))
                if subtype not in _ALLOWED_ANNOTATION_SUBTYPES:
                    element = (
                        "embedded-attachments"
                        if subtype == "/FileAttachment"
                        else "annotations"
                    )
                    result.findings.append(
                        ProhibitedFinding(
                            element=element,
                            detail=f"page {page_index} has a prohibited "
                            f"{subtype or 'untyped'} annotation "
                            "(only link annotations are permitted)",
                        )
                    )

    return result


def scrub_prohibited_elements(
    input_path: str | Path, output_path: str | Path
) -> DocumentScanResult:
    """Remove every scrubbable prohibited element, writing a new PDF.

    Raises FloridaDocumentError for unscrubbable findings (a password-locked
    file cannot be repaired without its password). The rewrite also purges
    orphaned objects left by incremental updates ("hidden deleted items —
    purge them"). Scrubbing is not PDF/A conversion; run
    ecfiler.pdf.converter.convert_to_pdfa on the scrubbed output.
    """
    inp, out = Path(input_path), Path(output_path)
    scan = scan_prohibited_elements(inp)
    unfixable = [f for f in scan.findings if not f.scrubbable]
    if unfixable:
        raise FloridaDocumentError(
            "cannot scrub: " + "; ".join(f.detail for f in unfixable)
        )

    with pikepdf.open(inp) as pdf:
        root = pdf.Root
        for key in ("/AcroForm", "/OpenAction", "/AA", "/PieceInfo"):
            if key in root:
                del root[key]
        names = root.get("/Names", None)
        if names is not None:
            for key in ("/JavaScript", "/EmbeddedFiles"):
                if key in names:
                    del names[key]
        for page in pdf.pages:
            for key in ("/Thumb", "/AA", "/PieceInfo"):
                if key in page:
                    del page[key]
            annots = page.get("/Annots", None)
            if annots is not None:
                kept = [
                    a
                    for a in annots
                    if str(a.get("/Subtype", "")) in _ALLOWED_ANNOTATION_SUBTYPES
                ]
                del page["/Annots"]
                if kept:
                    page["/Annots"] = pdf.make_indirect(pikepdf.Array(kept))
        # A full save drops encryption and unreferenced (deleted) objects.
        pdf.save(out)

    after = scan_prohibited_elements(out)
    if not after.clean:
        raise FloridaDocumentError(
            "scrub left prohibited elements behind: "
            + "; ".join(f.detail for f in after.findings)
        )
    return after


def validate_submission_files(
    submission: Submission,
    files: dict[str, str | Path],
    *,
    limit_mb: int = TRIAL_SUBMISSION_LIMIT_MB,
) -> None:
    """Hard-validate a submission's real files against the Portal rules.

    `files` maps Document.filename → path on disk. Raises FloridaDocumentError
    on any violation: missing file, forbidden filename, prohibited elements,
    or the whole submission exceeding the size cap (the 50 MB limit is per
    submission, not per document — Standards §2.1.2).
    """
    submission.validate_documents()

    problems: list[str] = []
    total_bytes = 0
    for doc in submission.documents:
        problems.extend(validate_filename(doc.filename))
        path = files.get(doc.filename)
        if path is None:
            problems.append(f"no file provided for document {doc.filename!r}")
            continue
        p = Path(path)
        if not p.exists():
            problems.append(f"file missing on disk: {p}")
            continue
        total_bytes += p.stat().st_size
        scan = scan_prohibited_elements(p)
        problems.extend(f"{doc.filename}: {f.detail}" for f in scan.findings)

    total_mb = total_bytes / (1024 * 1024)
    if total_mb > limit_mb:
        problems.append(
            f"submission totals {total_mb:.1f} MB; the Portal caps a single "
            f"submission at {limit_mb} MB"
        )

    if problems:
        raise FloridaDocumentError(
            "submission violates Portal document rules:\n- " + "\n- ".join(problems)
        )


def prepare_document_for_portal(
    input_path: str | Path,
    output_path: str | Path,
    *,
    convert_pdfa: bool = True,
) -> Path:
    """Scrub prohibited elements, then convert to PDF/A (the Portal's
    preferred delivery format).

    Returns the path of the Portal-ready file. Raises FloridaDocumentError if
    the document cannot be made compliant. PDF/A conversion requires ocrmypdf
    (`pip install 'ecfiler[pdf-convert]'`); with convert_pdfa=False the
    scrubbed (but non-PDF/A) file is returned, which the Portal accepts and
    converts clerk-side per Standards §2.1.3.
    """
    out = Path(output_path)
    scrub_prohibited_elements(input_path, out)

    if convert_pdfa:
        from ecfiler.pdf.converter import convert_to_pdfa, is_ocrmypdf_available

        if not is_ocrmypdf_available():
            raise FloridaDocumentError(
                "PDF/A conversion requested but ocrmypdf is not installed; "
                "install 'ecfiler[pdf-convert]' or pass convert_pdfa=False"
            )
        pdfa_out = out.with_stem(out.stem + "_pdfa")
        result = convert_to_pdfa(out, pdfa_out)
        if not result.success:
            raise FloridaDocumentError(f"PDF/A conversion failed: {result.message}")
        return Path(result.output_path)

    return out
