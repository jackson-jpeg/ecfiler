"""Filing workflow state machine.

Orchestrates the complete filing process through safety gates,
from court selection to receipt capture.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from ecfiler.filing.events import get_common_events, search_events
from ecfiler.filing.models import (
    CaseInfo,
    CourtType,
    Document,
    DocumentValidation,
    EventCode,
    Filing,
    FilingReceipt,
    FilingStatus,
    RelatedEntry,
)

if TYPE_CHECKING:
    from ecfiler.config import AppConfig

console = Console()


class FilingWorkflow:
    """Manages the complete filing workflow with safety gates."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.filing: Filing | None = None
        self._claude = None
        self._browser = None

    def run(self) -> FilingReceipt | None:
        """Execute the full filing workflow.

        Returns a FilingReceipt on success, None on cancellation/failure.
        """
        try:
            # Step 1: Select court
            court_id, court_type = self._step_select_court()

            # Step 2: Enter case number
            case_info = self._step_enter_case(court_id)

            # Step 3: Select event code
            event = self._step_select_event(court_id, court_type)

            # Step 4: Select documents
            documents = self._step_select_documents()

            # Step 5: Validate documents (Safety Gate 1 & 2)
            documents = self._step_validate_documents(documents)

            # Step 6: Related filing (optional)
            related = self._step_related_entry()

            # Build filing record
            self.filing = Filing(
                court_id=court_id,
                court_type=CourtType(court_type),
                case=case_info,
                event=event,
                documents=documents,
                related_entry=related,
                status=FilingStatus.DOCUMENTS_VALIDATED,
            )

            # Step 7: Claude validation (Safety Gate 3 & 4)
            self._step_ai_validation()

            # Step 8: Attorney review (Safety Gate 5)
            if not self._step_attorney_review():
                console.print("[yellow]Filing cancelled.[/yellow]")
                self.filing.status = FilingStatus.CANCELLED
                return None

            # Step 9: Browser filing (Safety Gate 6)
            if self.config.general.dry_run:
                console.print(
                    "\n[yellow]DRY RUN — stopping before submission.[/yellow]"
                )
                self.filing.status = FilingStatus.AWAITING_REVIEW
                return None

            receipt = self._step_submit_filing()

            # Step 10: Save receipt (Safety Gate 7)
            self._step_save_receipt(receipt)

            return receipt

        except KeyboardInterrupt:
            console.print("\n[yellow]Filing cancelled by user.[/yellow]")
            return None
        except Exception as e:
            console.print(f"\n[red]Filing error: {e}[/red]")
            return None

    # --- Individual workflow steps ---

    def _step_select_court(self) -> tuple[str, str]:
        """Step 1: Select the court."""
        from ecfiler.courts.registry import CourtRegistry

        registry = CourtRegistry()

        default = self.config.general.default_court
        if default:
            try:
                court = registry.get(default)
                console.print(
                    f"\n  Court: [bold]{court.profile.name}[/bold] ({default})"
                )
                if not Confirm.ask("  Use this court?", default=True):
                    default = ""
            except (KeyError, ValueError) as e:
                console.print(f"  [yellow]Default court '{default}' not found: {e}[/yellow]")
                default = ""

        if not default:
            console.print(f"\n  [dim]{registry.count} courts available[/dim]")
            query = Prompt.ask("  Search courts (name or ID)")
            results = registry.search(query)
            if not results:
                console.print("[red]  No courts found.[/red]")
                return self._step_select_court()

            for i, r in enumerate(results[:10], 1):
                console.print(f"  [{i}] {r['name']} ({r['court_id']}) [{r['type']}]")

            choice = Prompt.ask(
                "  Select", choices=[str(i) for i in range(1, min(11, len(results) + 1))]
            )
            selected = results[int(choice) - 1]
            default = selected["court_id"]

        court = registry.get(default)
        return court.profile.court_id, court.profile.court_type

    def _step_enter_case(self, court_id: str) -> CaseInfo:
        """Step 2: Enter case number and look up case info."""
        case_number = Prompt.ask("\n  Case number")

        console.print(f"  [dim]Looking up case {case_number}...[/dim]")

        # Try PACER Case Locator API for case details
        try:
            from ecfiler.pacer_auth import PacerAuth
            from ecfiler.pacer_search import PacerSearch

            auth = PacerAuth(self.config.pacer.username)
            token = auth.get_token()
            search = PacerSearch(token)
            result = search.get_case(court_id, case_number)
            search.close()
            auth.close()

            if result:
                console.print(f"  [green]✓[/green] {result.display}")
                return CaseInfo(
                    case_number=result.case_number,
                    title=result.case_title,
                    judge=result.judge,
                    status="open" if result.is_open else "closed",
                )
            else:
                console.print("  [yellow]Case not found in PACER — continuing with manual entry[/yellow]")
        except Exception as e:
            console.print(f"  [dim]PACER lookup unavailable ({type(e).__name__}) — continuing[/dim]")

        return CaseInfo(case_number=case_number)

    def _step_select_event(self, court_id: str, court_type: str) -> EventCode:
        """Step 3: Select event code (with Claude assistance)."""
        console.print("\n  [bold]What are you filing?[/bold]")
        console.print("  [1] Search by description")
        console.print("  [2] Browse categories")
        console.print("  [3] Describe in plain English (AI-assisted)")

        choice = Prompt.ask("  Select", choices=["1", "2", "3"], default="3")

        if choice == "1":
            query = Prompt.ask("  Search")
            matches = search_events(query, court_type)
            if not matches:
                console.print("  [yellow]No matches. Try describing it instead.[/yellow]")
                return self._step_select_event(court_id, court_type)
            return self._pick_event(matches)

        elif choice == "2":
            from ecfiler.filing.events import get_event_categories

            categories = get_event_categories(court_type)
            for i, cat in enumerate(categories, 1):
                console.print(f"  [{i}] {cat}")
            cat_choice = Prompt.ask(
                "  Category",
                choices=[str(i) for i in range(1, len(categories) + 1)],
            )
            selected_cat = categories[int(cat_choice) - 1]
            events = [
                e
                for e in get_common_events(court_type)
                if e.category == selected_cat
            ]
            return self._pick_event(events)

        else:
            description = Prompt.ask("  Describe your filing")
            return self._ai_suggest_event(court_id, court_type, description)

    def _pick_event(self, events: list[EventCode]) -> EventCode:
        """Display events and let user pick one."""
        for i, e in enumerate(events[:15], 1):
            console.print(f"  [{i}] {e.description} (code: {e.code})")

        choice = Prompt.ask(
            "  Select",
            choices=[str(i) for i in range(1, min(16, len(events) + 1))],
        )
        return events[int(choice) - 1]

    def _ai_suggest_event(
        self, court_id: str, court_type: str, description: str
    ) -> EventCode:
        """Use Claude to suggest an event code from natural language."""
        try:
            claude = self._get_claude()
            events = get_common_events(court_type)
            codes_list = [
                {"code": e.code, "description": e.description} for e in events
            ]

            result = claude.suggest_event_code(
                court_id, court_type, description, codes_list
            )

            if result.get("parse_error"):
                console.print(
                    "  [yellow]AI couldn't parse response. Falling back to search.[/yellow]"
                )
                return self._step_select_event(court_id, court_type)

            rec_code = result.get("recommended_code", "")
            rec_desc = result.get("recommended_description", "")
            confidence = result.get("confidence", "unknown")
            reasoning = result.get("reasoning", "")

            console.print(
                f"\n  [cyan]AI suggests:[/cyan] {rec_desc} (code: {rec_code})"
            )
            console.print(f"  [dim]Confidence: {confidence}[/dim]")
            if reasoning:
                console.print(f"  [dim]Reason: {reasoning}[/dim]")

            if Confirm.ask("  Use this event code?", default=True):
                return EventCode(code=rec_code, description=rec_desc)
            else:
                return self._step_select_event(court_id, court_type)

        except (anthropic.APIError, anthropic.APIConnectionError) as e:
            console.print(f"  [yellow]Claude API error: {e}. Falling back to search.[/yellow]")
            query = Prompt.ask("  Search events manually")
            matches = search_events(query, court_type)
            return self._pick_event(matches) if matches else self._step_select_event(court_id, court_type)
        except Exception as e:
            console.print(f"  [yellow]AI unavailable ({type(e).__name__}: {e}). Falling back to search.[/yellow]")
            query = Prompt.ask("  Search events manually")
            matches = search_events(query, court_type)
            return self._pick_event(matches) if matches else self._step_select_event(court_id, court_type)

    def _step_select_documents(self) -> list[Document]:
        """Step 4: Select PDF documents to file."""
        documents: list[Document] = []

        main_path = Prompt.ask("\n  Main document path")
        main_path = main_path.strip().strip("'\"")
        documents.append(
            Document(file_path=main_path, description="Main document", is_main=True)
        )

        while Confirm.ask("  Add attachment?", default=False):
            att_path = Prompt.ask("  Attachment path").strip().strip("'\"")
            att_desc = Prompt.ask("  Description", default="")
            documents.append(
                Document(file_path=att_path, description=att_desc, is_main=False)
            )

        return documents

    def _step_validate_documents(self, documents: list[Document]) -> list[Document]:
        """Step 5: Validate all documents (Safety Gates 1 & 2)."""
        from ecfiler.pdf.validator import validate_pdf

        console.print("\n  [bold]Validating documents...[/bold]")

        all_valid = True
        for doc in documents:
            result = validate_pdf(
                doc.file_path,
                max_size_mb=self.config.pdf.max_file_size_mb,
            )
            doc.validation = DocumentValidation(
                valid=result.valid,
                file_size_mb=result.file_size_mb,
                page_count=result.page_count,
                has_text=result.has_text,
                is_encrypted=result.is_encrypted,
                errors=result.errors,
                warnings=result.warnings,
            )

            if result.valid:
                console.print(f"  [green]✓[/green] {doc.filename}: {result.summary}")
            else:
                console.print(f"  [red]✗[/red] {doc.filename}: {result.summary}")
                for err in result.errors:
                    console.print(f"    [red]{err}[/red]")
                all_valid = False

            for warn in result.warnings:
                console.print(f"    [yellow]⚠ {warn}[/yellow]")

        if not all_valid:
            if not Confirm.ask(
                "\n  [yellow]Some documents have errors. Continue anyway?[/yellow]",
                default=False,
            ):
                raise KeyboardInterrupt("Validation failed")

        # Redaction check (Safety Gate 2)
        if self.config.pdf.redaction_check:
            self._run_redaction_check(documents)

        return documents

    def _run_redaction_check(self, documents: list[Document]) -> None:
        """Run redaction scanning on documents."""
        from ecfiler.pdf.redaction_check import scan_document
        from ecfiler.pdf.validator import extract_text

        console.print("\n  [dim]Scanning for redaction issues...[/dim]")

        for doc in documents:
            try:
                text = extract_text(doc.file_path)
                report = scan_document(text, claude_client=self._get_claude_safe())
                if report.has_issues:
                    console.print(
                        f"  [yellow]⚠ {doc.filename}: "
                        f"{len(report.issues)} potential redaction issue(s)[/yellow]"
                    )
                    for issue in report.issues:
                        console.print(
                            f"    [{issue.confidence}] {issue.issue_type}: "
                            f"{issue.text[:50]} — {issue.suggestion}"
                        )
                else:
                    console.print(
                        f"  [green]✓[/green] {doc.filename}: No redaction issues"
                    )
            except FileNotFoundError:
                console.print(
                    f"  [red]File not found: {doc.file_path}[/red]"
                )
            except Exception as e:
                console.print(
                    f"  [dim]Could not scan {doc.filename} for redaction ({type(e).__name__})[/dim]"
                )

    def _step_related_entry(self) -> RelatedEntry | None:
        """Step 6: Select related docket entry (optional)."""
        if Confirm.ask("\n  Relate to existing docket entry?", default=False):
            number = Prompt.ask("  Docket entry number")
            desc = Prompt.ask("  Description", default="")
            return RelatedEntry(docket_number=number, description=desc)
        return None

    def _step_ai_validation(self) -> None:
        """Step 7: Claude validates the filing package (Safety Gates 3 & 4)."""
        if not self.filing:
            return

        try:
            claude = self._get_claude()
            main_doc = self.filing.main_document

            from ecfiler.pdf.validator import extract_text, extract_title

            doc_title = extract_title(main_doc.file_path) if main_doc else ""
            first_page = ""
            if main_doc:
                text = extract_text(main_doc.file_path, max_pages=1)
                first_page = text[:2000]

            result = claude.validate_filing_package(
                court_id=self.filing.court_id,
                court_type=self.filing.court_type.value,
                event_code=self.filing.event.code,
                event_description=self.filing.event.description,
                document_title=doc_title,
                first_page_text=first_page,
                attachment_names=[d.filename for d in self.filing.attachments],
            )

            if not result.get("parse_error"):
                for warning in result.get("warnings", []):
                    console.print(f"  [yellow]⚠ AI: {warning}[/yellow]")
                for error in result.get("errors", []):
                    console.print(f"  [red]✗ AI: {error}[/red]")
                for suggestion in result.get("suggestions", []):
                    console.print(f"  [dim]💡 {suggestion}[/dim]")

                if result.get("valid"):
                    console.print(
                        "  [green]✓ AI validation passed[/green]"
                    )
        except Exception as e:
            console.print(f"  [dim]AI validation unavailable ({type(e).__name__}) — proceeding[/dim]")

    def _step_attorney_review(self) -> bool:
        """Step 8: Attorney review and confirmation (Safety Gate 5).

        Returns True if attorney confirms, False to cancel.
        """
        if not self.filing:
            return False

        self.filing.status = FilingStatus.AWAITING_REVIEW

        console.print()
        console.print(
            Panel(
                "[bold red]FILING REVIEW — ATTORNEY APPROVAL REQUIRED[/bold red]",
                border_style="red",
            )
        )

        table = Table(show_header=False, border_style="dim")
        table.add_column("Field", style="bold")
        table.add_column("Value")

        table.add_row("Court", f"{self.filing.court_id} ({self.filing.court_type.value})")
        table.add_row("Case", self.filing.case.case_number)
        if self.filing.case.title:
            table.add_row("Title", self.filing.case.title)
        table.add_row("Event", f"{self.filing.event.description} ({self.filing.event.code})")

        for doc in self.filing.documents:
            status = "[green]✓[/green]" if doc.is_valid else "[red]✗[/red]"
            label = "Document" if doc.is_main else "Attachment"
            size = f"{doc.validation.file_size_mb:.1f}MB" if doc.validation else "?"
            table.add_row(label, f"{status} {doc.filename} ({size})")

        if self.filing.related_entry:
            table.add_row(
                "Related",
                f"Docket #{self.filing.related_entry.docket_number} "
                f"{self.filing.related_entry.description}",
            )

        if self.config.general.dry_run:
            table.add_row("Mode", "[yellow]DRY RUN[/yellow]")

        console.print(table)
        console.print()

        confirm = Prompt.ask(
            "  Type [bold]CONFIRM[/bold] to submit, or [bold]CANCEL[/bold] to abort"
        )

        if confirm.upper() == "CONFIRM":
            self.filing.status = FilingStatus.CONFIRMED
            return True

        return False

    def _step_submit_filing(self) -> FilingReceipt:
        """Step 9: Submit filing via browser automation (Safety Gate 6)."""
        if not self.filing:
            raise RuntimeError("No filing to submit")

        from ecfiler.browser.session import BrowserSession
        from ecfiler.courts.registry import CourtRegistry

        console.print("\n  [bold]Submitting filing...[/bold]")

        registry = CourtRegistry()
        court = registry.get(self.filing.court_id)

        with BrowserSession(headless=True) as browser:
            # Authenticate
            console.print("  [dim]Authenticating with PACER...[/dim]")
            try:
                from ecfiler.pacer_auth import PacerAuth

                auth = PacerAuth(self.config.pacer.username)
                token = auth.get_token()
                browser.inject_pacer_token(token, court.profile.domain)
            except Exception as e:
                console.print(f"  [yellow]Token auth failed ({e}), trying form login...[/yellow]")
                from ecfiler.pacer_auth import PacerAuth as PacerAuthFallback

                try:
                    fallback_auth = PacerAuthFallback(self.config.pacer.username)
                    password = fallback_auth.get_password()
                except Exception:
                    raise RuntimeError(
                        "PACER login failed: no stored password. "
                        "Run 'ecfiler' and choose 'Setup Credentials' first."
                    )
                if not browser.login_via_form(
                    court.profile.login_url,
                    self.config.pacer.username,
                    password,
                ):
                    raise RuntimeError("PACER login failed")

            page = browser.page

            # Navigate to filing
            console.print("  [dim]Navigating to filing page...[/dim]")
            court.navigate_to_filing(page)
            browser.screenshot("filing_page")

            # Enter case
            console.print("  [dim]Entering case number...[/dim]")
            court.enter_case_number(page, self.filing.case.case_number)
            browser.screenshot("case_entered")

            # Select event
            console.print("  [dim]Selecting event type...[/dim]")
            court.select_event(page, self.filing.event.code)
            browser.screenshot("event_selected")

            # Upload documents
            main_doc = self.filing.main_document
            if main_doc:
                console.print("  [dim]Uploading main document...[/dim]")
                court.upload_document(page, main_doc.file_path)
                browser.screenshot("document_uploaded")

            for att in self.filing.attachments:
                console.print(f"  [dim]Uploading attachment: {att.filename}...[/dim]")
                court.upload_attachment(page, att.file_path, att.description)

            # Related entry
            if self.filing.related_entry:
                court.select_related_entry(
                    page, self.filing.related_entry.docket_number
                )

            browser.screenshot("form_filled")

            # Safety Gate 6: Show final confirmation screenshot
            console.print(
                "\n  [bold yellow]Final CM/ECF confirmation page:[/bold yellow]"
            )
            confirmation_path = browser.screenshot("final_confirmation")
            console.print(f"  Screenshot: {confirmation_path}")

            confirm_text = court.get_confirmation_text(page)
            console.print(f"  [dim]{confirm_text[:500]}[/dim]")

            final_confirm = Prompt.ask(
                "\n  [bold red]FINAL CHECK:[/bold red] Submit to CM/ECF? "
                "Type [bold]YES[/bold] to proceed"
            )

            if final_confirm.upper() != "YES":
                console.print("  [yellow]Aborted at final confirmation.[/yellow]")
                self.filing.status = FilingStatus.CANCELLED
                raise KeyboardInterrupt("Cancelled at final submit")

            # Submit
            console.print("  [dim]Submitting...[/dim]")
            court.click_final_submit(page)
            browser.screenshot("submitted")

            # Capture receipt
            receipt_info = court.get_receipt_info(page)
            receipt_path = browser.save_receipt(
                self.filing.case.case_number, "pending"
            )

            self.filing.status = FilingStatus.SUBMITTED

            return FilingReceipt(
                court_id=self.filing.court_id,
                case_number=self.filing.case.case_number,
                event_description=self.filing.event.description,
                confirmation_text=receipt_info.get("page_text", ""),
                receipt_path=str(receipt_path),
            )

    def _step_save_receipt(self, receipt: FilingReceipt) -> None:
        """Step 10: Save receipt and log to history (Safety Gate 7)."""
        from ecfiler.storage.history import FilingHistory

        history = FilingHistory()
        history.log_filing(receipt)

        console.print(
            Panel(
                f"[bold green]✅ FILED SUCCESSFULLY[/bold green]\n\n"
                f"Court: {receipt.court_id}\n"
                f"Case: {receipt.case_number}\n"
                f"Event: {receipt.event_description}\n"
                f"Receipt: {receipt.receipt_path}",
                border_style="green",
            )
        )

        self.filing.status = FilingStatus.RECEIPT_SAVED

    # --- Helpers ---

    def _get_claude(self):
        """Get or create Claude client."""
        if self._claude is None:
            from ecfiler.claude_client import ClaudeClient

            self._claude = ClaudeClient(
                api_key=self.config.claude_api_key,
                model=self.config.general.claude_model,
            )
        return self._claude

    def _get_claude_safe(self):
        """Get Claude client, returning None if unavailable."""
        try:
            return self._get_claude()
        except Exception:
            return None
