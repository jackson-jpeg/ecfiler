"""Smart Filing Agent — drop a PDF, get a complete filing.

This is the AI-native filing experience. Instead of walking through
menus and forms, the attorney drops a document and the agent:

1. Reads the document
2. Extracts all filing metadata (case, court, party, event type)
3. Validates the PDF
4. Scans for redaction issues
5. Matches to a CM/ECF event code
6. Presents a fully-formed filing for one-click confirmation

The attorney's job is reduced to: review and CONFIRM.
"""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ecfiler.agent.document_analyzer import DocumentAnalysis, analyze_document
from ecfiler.config import AppConfig
from ecfiler.filing.events import get_common_events, search_events
from ecfiler.filing.models import (
    CaseInfo,
    CourtType,
    Document,
    DocumentValidation,
    EventCode,
    Filing,
    FilingParty,
    FilingReceipt,
    FilingStatus,
    RelatedEntry,
)
from ecfiler.logging import get_logger

logger = get_logger(__name__)
console = Console()


class SmartFiler:
    """AI-native filing agent.

    Usage:
        filer = SmartFiler(config)
        receipt = filer.file("/path/to/motion.pdf")
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config

    def file(self, pdf_path: str, dry_run: bool = False) -> FilingReceipt | None:
        """Analyze a document and prepare a complete filing.

        Args:
            pdf_path: Path to the PDF to file
            dry_run: If True, stop before submission

        Returns:
            FilingReceipt on success, None on cancel
        """
        path = Path(pdf_path)
        if not path.exists():
            console.print(f"[red]File not found: {pdf_path}[/red]")
            return None

        console.print(
            Panel(
                f"[bold cyan]Smart Filing[/bold cyan]\n"
                f"[dim]Analyzing: {path.name}[/dim]",
                border_style="cyan",
            )
        )

        # Step 1: Validate PDF
        console.print("\n  [dim]Validating PDF...[/dim]")
        from ecfiler.pdf.validator import validate_pdf, extract_text

        validation = validate_pdf(pdf_path)
        if not validation.valid:
            console.print(f"  [red]PDF invalid: {', '.join(validation.errors)}[/red]")
            return None
        console.print(f"  [green]✓[/green] {validation.summary}")

        # Step 2: Extract text and analyze with AI
        console.print("  [dim]Reading document...[/dim]")
        text = extract_text(pdf_path, max_pages=30)

        console.print("  [dim]AI analyzing document...[/dim]")
        try:
            analysis = analyze_document(
                text,
                api_key=self.config.claude_api_key,
                model=self.config.general.claude_model,
            )
        except Exception as e:
            console.print(f"  [red]Analysis failed: {e}[/red]")
            console.print("  [dim]Falling back to manual filing mode.[/dim]")
            from ecfiler.filing.workflow import FilingWorkflow
            return FilingWorkflow(self.config).run()

        # Step 3: Present analysis
        self._show_analysis(analysis)

        # Step 4: Let attorney correct anything
        analysis = self._review_and_correct(analysis)

        # Step 5: Redaction scan
        console.print("\n  [dim]Scanning for redaction issues...[/dim]")
        from ecfiler.pdf.redaction_check import scan_document
        redaction = scan_document(text)
        if redaction.has_issues:
            console.print(f"  [yellow]⚠ {len(redaction.issues)} potential redaction issue(s)[/yellow]")
            for issue in redaction.issues:
                console.print(f"    [{issue.confidence}] {issue.issue_type}: {issue.text[:50]}")
        else:
            console.print("  [green]✓[/green] No redaction issues")

        # Step 6: Match event code
        event = self._resolve_event_code(analysis)

        # Step 7: Build filing
        filing = Filing(
            court_id=analysis.court_id,
            court_type=self._infer_court_type(analysis.court_id),
            case=CaseInfo(
                case_number=analysis.case_number,
                title=analysis.case_caption,
            ),
            event=event,
            documents=[
                Document(
                    file_path=pdf_path,
                    description=analysis.document_type_specific,
                    is_main=True,
                    validation=DocumentValidation(
                        valid=validation.valid,
                        file_size_mb=validation.file_size_mb,
                        page_count=validation.page_count,
                        has_text=validation.has_text,
                        is_encrypted=validation.is_encrypted,
                    ),
                )
            ],
            filing_party=FilingParty(
                party_name=analysis.filing_party_name,
                party_role=analysis.filing_party_role,
                attorney_name=analysis.attorney_name or self.config.attorney.name,
                attorney_bar_number=analysis.attorney_bar_number or self.config.attorney.bar_number,
            ),
            is_response=analysis.is_response,
            related_entry=(
                RelatedEntry(
                    docket_number=analysis.responds_to_docket_number,
                    description=analysis.responds_to,
                )
                if analysis.responds_to_docket_number
                else None
            ),
            status=FilingStatus.AWAITING_REVIEW,
        )

        # Step 8: Completeness warnings
        warnings = self._check_completeness(analysis, filing)
        if warnings:
            console.print("\n  [bold yellow]Completeness warnings:[/bold yellow]")
            for w in warnings:
                console.print(f"    [yellow]⚠ {w}[/yellow]")

        # Step 9: Pre-flight checks
        from ecfiler.filing.preflight import run_preflight

        console.print("\n  [dim]Running pre-flight checks...[/dim]")
        preflight = run_preflight(filing)
        for err in preflight.errors:
            console.print(f"  [red]✗ {err}[/red]")
        for warn in preflight.warnings:
            console.print(f"  [yellow]⚠ {warn}[/yellow]")
        if preflight.passed:
            console.print("  [green]✓[/green] Pre-flight checks passed")
        else:
            console.print(f"\n  [red]Pre-flight FAILED ({len(preflight.errors)} errors)[/red]")
            if not Confirm.ask("  Continue anyway?", default=False):
                return None

        # Step 10: Final review — one screen, one CONFIRM
        if not self._final_review(filing, analysis):
            console.print("[yellow]Filing cancelled.[/yellow]")
            return None

        if dry_run or self.config.general.dry_run:
            console.print("\n  [yellow]DRY RUN — stopping before submission.[/yellow]")
            return None

        # Step 11: Submit via the full workflow (with error recovery)
        from ecfiler.filing.workflow import FilingWorkflow
        workflow = FilingWorkflow(self.config)
        workflow.filing = filing
        receipt = workflow._step_submit_filing()
        if receipt:
            workflow._step_save_receipt(receipt)
        return receipt

    def _show_analysis(self, analysis: DocumentAnalysis) -> None:
        """Display what the AI extracted."""
        score = analysis.completeness_score
        if score >= 80:
            color = "green"
            label = "High"
        elif score >= 50:
            color = "yellow"
            label = "Partial"
        else:
            color = "red"
            label = "Low"

        console.print(
            f"\n  [bold]AI Extraction[/bold] — "
            f"[{color}]{label} ({score}% auto-filled)[/{color}]"
        )

        table = Table(show_header=False, border_style="dim", padding=(0, 2))
        table.add_column("Field", style="bold", width=16)
        table.add_column("Extracted Value")
        table.add_column("", width=3)

        def row(label: str, value: str) -> None:
            icon = "[green]✓[/green]" if value else "[red]?[/red]"
            table.add_row(label, value or "[dim]not found[/dim]", icon)

        row("Document Type", analysis.document_type_specific)
        row("Case Number", analysis.case_number)
        row("Court", f"{analysis.court_id} — {analysis.court_name}" if analysis.court_id else analysis.court_name)
        row("Caption", analysis.case_caption)
        row("Filed By", analysis.filing_party_name)
        row("Party Role", analysis.filing_party_role)
        row("Attorney", analysis.attorney_name)

        if analysis.is_response:
            row("Response To", analysis.responds_to)
            row("Re: Docket #", analysis.responds_to_docket_number)

        row("Category", analysis.suggested_event_code_category)
        row("Cert. of Service", "Yes" if analysis.has_certificate_of_service else "No")
        row("Signature", "Yes" if analysis.has_signature else "No")

        console.print(table)

    def _review_and_correct(self, analysis: DocumentAnalysis) -> DocumentAnalysis:
        """Let the attorney correct any extracted fields."""
        if analysis.completeness_score >= 80:
            if Confirm.ask("\n  All fields look correct?", default=True):
                return analysis
        else:
            console.print(
                f"\n  [yellow]Missing fields: {', '.join(analysis.missing_fields)}[/yellow]"
            )

        # Walk through missing/uncertain fields
        if not analysis.case_number:
            analysis.case_number = Prompt.ask("  Case number")
        if not analysis.court_id:
            analysis.court_id = Prompt.ask("  Court ID (e.g., nysd)")
        if not analysis.filing_party_name:
            analysis.filing_party_name = Prompt.ask("  Filing party name")
        if not analysis.filing_party_role:
            analysis.filing_party_role = Prompt.ask(
                "  Party role",
                choices=["plaintiff", "defendant", "petitioner", "respondent", "debtor", "other"],
            )
        if not analysis.document_type_specific:
            analysis.document_type_specific = Prompt.ask("  Document type")

        return analysis

    def _resolve_event_code(self, analysis: DocumentAnalysis) -> EventCode:
        """Match the analyzed document to a CM/ECF event code."""
        court_type = self._infer_court_type(analysis.court_id).value
        desc = analysis.document_type_specific or analysis.document_type

        # Try direct search first
        matches = search_events(desc, court_type)
        if matches:
            best = matches[0]
            console.print(f"\n  [cyan]Event code:[/cyan] {best.description} ({best.code})")
            if Confirm.ask("  Correct?", default=True):
                return best

        # Try AI suggestion
        try:
            from ecfiler.claude_client import ClaudeClient
            claude = ClaudeClient(
                api_key=self.config.claude_api_key,
                model=self.config.general.claude_model,
            )
            events = get_common_events(court_type)
            codes = [{"code": e.code, "description": e.description} for e in events]
            result = claude.suggest_event_code(analysis.court_id, court_type, desc, codes)
            claude.close()

            if not result.get("parse_error"):
                code = result.get("recommended_code", "")
                description = result.get("recommended_description", "")
                console.print(f"  [cyan]AI suggests:[/cyan] {description} ({code})")
                if Confirm.ask("  Use this?", default=True):
                    return EventCode(code=code, description=description)
        except Exception:
            pass

        # Manual fallback
        console.print("  [dim]Select event code manually:[/dim]")
        events = get_common_events(court_type)
        for i, e in enumerate(events[:15], 1):
            console.print(f"    [{i}] {e.description}")
        choice = Prompt.ask("  Select", choices=[str(i) for i in range(1, 16)])
        return events[int(choice) - 1]

    def _check_completeness(self, analysis: DocumentAnalysis, filing: Filing) -> list[str]:
        """Check for common filing completeness issues."""
        warnings: list[str] = []

        if not analysis.has_signature:
            warnings.append("No signature block detected in document")

        if not analysis.has_certificate_of_service:
            event_desc = filing.event.description.lower()
            needs_cos = any(w in event_desc for w in ["motion", "brief", "memo", "reply", "response"])
            if needs_cos:
                warnings.append("No certificate of service detected — most filings require one")

        if analysis.is_response and not analysis.responds_to_docket_number:
            warnings.append("Response filing but no docket number for the entry being responded to")

        if analysis.document_type in ("motion",) and not analysis.has_proposed_order:
            warnings.append("Motion filed without a proposed order — some courts require one")

        return warnings

    def _final_review(self, filing: Filing, analysis: DocumentAnalysis) -> bool:
        """One-screen final review."""
        console.print()
        console.print(
            Panel(
                "[bold red]FILING REVIEW — ATTORNEY APPROVAL REQUIRED[/bold red]",
                border_style="red",
            )
        )

        table = Table(show_header=False, border_style="dim")
        table.add_column("", style="bold", width=14)
        table.add_column("")

        table.add_row("Court", f"{filing.court_id} ({filing.court_type.value})")
        table.add_row("Case", f"{filing.case.case_number}")
        if filing.case.title:
            table.add_row("Caption", filing.case.title)
        table.add_row("Event", f"{filing.event.description} ({filing.event.code})")

        if filing.filing_party:
            table.add_row("Filing for", filing.filing_party.display)

        if filing.is_response and filing.related_entry:
            table.add_row(
                "[yellow]Response to[/yellow]",
                f"Docket #{filing.related_entry.docket_number} {filing.related_entry.description}",
            )

        main = filing.main_document
        if main and main.validation:
            table.add_row(
                "Document",
                f"[green]✓[/green] {main.filename} ({main.validation.file_size_mb:.1f}MB, {main.validation.page_count} pages)",
            )

        table.add_row("Confidence", f"{analysis.confidence}")

        console.print(table)
        console.print()

        confirm = Prompt.ask("  Type [bold]CONFIRM[/bold] to file, or [bold]CANCEL[/bold]")
        return confirm.strip().upper() == "CONFIRM"

    def _infer_court_type(self, court_id: str) -> CourtType:
        """Infer court type from court ID."""
        if not court_id:
            return CourtType.DISTRICT
        try:
            from ecfiler.courts.registry import CourtRegistry
            registry = CourtRegistry()
            court = registry.get(court_id)
            return CourtType(court.profile.court_type)
        except Exception:
            if court_id.endswith("b"):
                return CourtType.BANKRUPTCY
            if court_id.startswith("ca"):
                return CourtType.APPELLATE
            return CourtType.DISTRICT
