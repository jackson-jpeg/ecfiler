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
    CaseOpeningData,
    CourtType,
    Document,
    DocumentValidation,
    EventCode,
    Filing,
    FilingParty,
    FilingReceipt,
    FilingStatus,
    PartyInfo,
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

            # Step 3b: Determine if this is a response to an existing entry
            is_response, related = self._step_response_context(event)

            # Step 3c: Select which party you're filing on behalf of
            filing_party = self._step_select_filing_party(case_info)

            # Step 3d: If opening a new case, collect case-opening data
            case_opening = None
            if event.category == "Initiating" or event.code in ("400", "401", "402", "B1", "B2"):
                case_opening = self._step_case_opening(court_type)

            # Step 4: Select documents
            documents = self._step_select_documents()

            # Step 5: Validate documents (Safety Gate 1 & 2)
            documents = self._step_validate_documents(documents)

            # Build filing record
            self.filing = Filing(
                court_id=court_id,
                court_type=CourtType(court_type),
                case=case_info,
                event=event,
                documents=documents,
                related_entry=related,
                filing_party=filing_party,
                is_response=is_response,
                case_opening=case_opening,
                status=FilingStatus.DOCUMENTS_VALIDATED,
            )

            # Step 6b: Pre-flight checks (catch problems before browser starts)
            self._step_preflight()

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
            self._offer_save_draft()
            return None
        except Exception as e:
            console.print(f"\n[red]Filing error: {e}[/red]")
            self._offer_save_draft()
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

    def _step_response_context(self, event: EventCode) -> tuple[bool, RelatedEntry | None]:
        """Step 3b: Determine if filing is a response to an existing docket entry.

        Responses, replies, oppositions, and answers typically relate to a
        specific prior docket entry. We ask proactively for these event types.
        """
        response_keywords = [
            "response", "opposition", "reply", "answer", "objection",
            "sur-reply", "brief in opposition", "memorandum in opposition",
        ]
        is_response_type = any(
            kw in event.description.lower() for kw in response_keywords
        )

        if is_response_type:
            console.print(
                f"\n  [bold]This is a {event.description} — what is it responding to?[/bold]"
            )
            number = Prompt.ask("  Docket entry number being responded to")
            desc = Prompt.ask("  Description of that entry", default="")
            related = RelatedEntry(docket_number=number, description=desc)

            # Confirm the linkage
            console.print(
                f"  [dim]Filing as response to Docket #{number} {desc}[/dim]"
            )
            if not Confirm.ask("  Correct?", default=True):
                return self._step_response_context(event)

            return True, related

        # For non-response filings, still offer the option
        if Confirm.ask("\n  Relate to existing docket entry?", default=False):
            number = Prompt.ask("  Docket entry number")
            desc = Prompt.ask("  Description", default="")
            return False, RelatedEntry(docket_number=number, description=desc)

        return False, None

    def _step_select_filing_party(self, case_info: CaseInfo) -> FilingParty | None:
        """Step 3c: Select which party the filer represents.

        CM/ECF requires you to identify which party you're filing on behalf of.
        """
        console.print("\n  [bold]Filing on behalf of:[/bold]")

        # If we have party info from PACER lookup, show them
        if case_info.parties:
            for i, party in enumerate(case_info.parties, 1):
                role_display = party.role.title()
                atty = f" (atty: {party.attorney})" if party.attorney else ""
                console.print(f"  [{i}] {party.name} — {role_display}{atty}")
            console.print(f"  [{len(case_info.parties) + 1}] Enter manually")

            choice = Prompt.ask(
                "  Select party",
                choices=[str(i) for i in range(1, len(case_info.parties) + 2)],
            )
            idx = int(choice) - 1
            if idx < len(case_info.parties):
                p = case_info.parties[idx]
                return FilingParty(
                    party_name=p.name,
                    party_role=p.role,
                    attorney_name=self.config.attorney.name,
                    attorney_bar_number=self.config.attorney.bar_number,
                )

        # Manual entry
        party_name = Prompt.ask("  Party name")
        party_role = Prompt.ask(
            "  Party role",
            choices=["plaintiff", "defendant", "petitioner", "respondent", "debtor", "creditor", "other"],
            default="plaintiff",
        )

        filing_party = FilingParty(
            party_name=party_name,
            party_role=party_role,
            attorney_name=self.config.attorney.name,
            attorney_bar_number=self.config.attorney.bar_number,
        )

        console.print(f"  [dim]Filing on behalf of: {filing_party.display}[/dim]")
        if not Confirm.ask("  Correct?", default=True):
            return self._step_select_filing_party(case_info)

        return filing_party

    def _step_case_opening(self, court_type: str) -> CaseOpeningData:
        """Step 3d: Collect case-opening data for new case filings.

        This is the most critical data entry step — errors here create
        a permanent, potentially incorrect court record.
        """
        console.print(
            Panel(
                "[bold yellow]NEW CASE FILING — Extra verification required[/bold yellow]\n"
                "[dim]All information below becomes part of the permanent court record.\n"
                "Please verify every field carefully.[/dim]",
                border_style="yellow",
            )
        )

        is_bankruptcy = court_type == "bankruptcy"

        if is_bankruptcy:
            return self._collect_bankruptcy_case_data()

        # Civil/Criminal case opening
        case_type = Prompt.ask(
            "  Case type",
            choices=["cv", "cr"],
            default="cv",
        )

        jurisdiction = ""
        demand = ""
        if case_type == "cv":
            jurisdiction = Prompt.ask(
                "  Jurisdiction basis",
                choices=["federal_question", "diversity", "other"],
                default="federal_question",
            )
            if jurisdiction == "diversity":
                demand = Prompt.ask("  Demand amount ($)", default="")

        cause = Prompt.ask("  Cause of action / statute", default="")
        jury = Prompt.ask(
            "  Jury demand",
            choices=["plaintiff", "defendant", "both", "none"],
            default="none",
        )

        # Collect parties
        console.print("\n  [bold]Plaintiffs / Petitioners:[/bold]")
        plaintiffs = self._collect_parties("plaintiff")

        console.print("\n  [bold]Defendants / Respondents:[/bold]")
        defendants = self._collect_parties("defendant")

        data = CaseOpeningData(
            case_type=case_type,
            cause_of_action=cause,
            jurisdiction_basis=jurisdiction,
            demand_amount=demand,
            jury_demand=jury,
            plaintiffs=plaintiffs,
            defendants=defendants,
        )

        # CRITICAL: Review all case-opening data before proceeding
        self._review_case_opening(data)

        return data

    def _collect_bankruptcy_case_data(self) -> CaseOpeningData:
        """Collect bankruptcy-specific case opening data."""
        chapter = Prompt.ask("  Chapter", choices=["7", "11", "12", "13"], default="7")

        console.print("\n  [bold]Debtor(s):[/bold]")
        debtors = self._collect_parties("debtor")

        asset = Confirm.ask("  Asset case?", default=False)
        creditors = Prompt.ask(
            "  Estimated number of creditors",
            choices=["1-49", "50-99", "100-199", "200-999", "1000+"],
            default="1-49",
        )
        assets = Prompt.ask("  Estimated assets", default="")
        liabilities = Prompt.ask("  Estimated liabilities", default="")

        data = CaseOpeningData(
            case_type="bk",
            chapter=chapter,
            plaintiffs=debtors,
            asset_case=asset,
            estimated_creditors=creditors,
            estimated_assets=assets,
            estimated_liabilities=liabilities,
        )

        self._review_case_opening(data)
        return data

    def _collect_parties(self, default_role: str) -> list[PartyInfo]:
        """Collect party information interactively."""
        parties: list[PartyInfo] = []
        while True:
            name = Prompt.ask(f"  Name{' (or Enter to finish)' if parties else ''}")
            if not name and parties:
                break
            if not name:
                console.print("  [red]At least one party required.[/red]")
                continue

            is_pro_se = Confirm.ask("  Pro se (self-represented)?", default=False)
            attorney = ""
            if not is_pro_se:
                attorney = Prompt.ask("  Attorney name", default=self.config.attorney.name)

            parties.append(PartyInfo(
                name=name,
                role=default_role,
                attorney=attorney,
                is_pro_se=is_pro_se,
            ))

            if not Confirm.ask("  Add another?", default=False):
                break

        return parties

    def _review_case_opening(self, data: CaseOpeningData) -> None:
        """Display case-opening data for verification. Requires explicit confirmation."""
        console.print(
            Panel("[bold]CASE OPENING DATA — VERIFY ALL FIELDS[/bold]", border_style="yellow")
        )

        table = Table(show_header=False, border_style="dim")
        table.add_column("Field", style="bold", width=20)
        table.add_column("Value")

        table.add_row("Case Type", data.case_type.upper())
        if data.cause_of_action:
            table.add_row("Cause of Action", data.cause_of_action)
        if data.jurisdiction_basis:
            table.add_row("Jurisdiction", data.jurisdiction_basis)
        if data.demand_amount:
            table.add_row("Demand", f"${data.demand_amount}")
        if data.jury_demand:
            table.add_row("Jury Demand", data.jury_demand)
        if data.chapter:
            table.add_row("Chapter", data.chapter)
        if data.estimated_creditors:
            table.add_row("Est. Creditors", data.estimated_creditors)

        console.print(table)

        if data.plaintiffs:
            role_label = "Debtors" if data.is_bankruptcy else "Plaintiffs"
            console.print(f"\n  [bold]{role_label}:[/bold]")
            for p in data.plaintiffs:
                atty = f" (pro se)" if p.is_pro_se else f" (atty: {p.attorney})"
                console.print(f"    {p.name}{atty}")

        if data.defendants:
            console.print("\n  [bold]Defendants:[/bold]")
            for p in data.defendants:
                atty = f" (pro se)" if p.is_pro_se else f" (atty: {p.attorney})"
                console.print(f"    {p.name}{atty}")

        console.print()
        if not Confirm.ask(
            "  [bold yellow]Is all case-opening information correct?[/bold yellow]",
            default=False,
        ):
            raise KeyboardInterrupt("Case opening data rejected by attorney")

    def _step_preflight(self) -> None:
        """Step 6b: Run pre-flight checks before browser automation."""
        if not self.filing:
            return

        from ecfiler.filing.preflight import run_preflight

        console.print("\n  [dim]Running pre-flight checks...[/dim]")
        result = run_preflight(self.filing)

        for err in result.errors:
            console.print(f"  [red]✗ {err}[/red]")
        for warn in result.warnings:
            console.print(f"  [yellow]⚠ {warn}[/yellow]")

        if result.passed:
            console.print(f"  [green]✓[/green] Pre-flight checks passed")
        else:
            console.print(f"\n  [red]Pre-flight checks FAILED ({len(result.errors)} errors)[/red]")
            if not Confirm.ask("  Continue anyway?", default=False):
                raise KeyboardInterrupt("Pre-flight checks failed")

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
        if self.filing.case.judge:
            table.add_row("Judge", self.filing.case.judge)
        table.add_row("Event", f"{self.filing.event.description} ({self.filing.event.code})")

        # Filing party
        if self.filing.filing_party:
            table.add_row("Filing for", self.filing.filing_party.display)

        # Response context
        if self.filing.is_response and self.filing.related_entry:
            table.add_row(
                "[yellow]Response to[/yellow]",
                f"Docket #{self.filing.related_entry.docket_number} "
                f"{self.filing.related_entry.description}",
            )
        elif self.filing.related_entry:
            table.add_row(
                "Related to",
                f"Docket #{self.filing.related_entry.docket_number} "
                f"{self.filing.related_entry.description}",
            )

        # Documents
        for doc in self.filing.documents:
            status = "[green]✓[/green]" if doc.is_valid else "[red]✗[/red]"
            label = "Document" if doc.is_main else "Attachment"
            size = f"{doc.validation.file_size_mb:.1f}MB" if doc.validation else "?"
            table.add_row(label, f"{status} {doc.filename} ({size})")

        # Case opening warning
        if self.filing.is_case_opening:
            table.add_row(
                "[bold yellow]NEW CASE[/bold yellow]",
                "[bold yellow]This filing opens a new case — verify all data above[/bold yellow]",
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

            from ecfiler.browser.recovery import (
                check_page_state,
                retry_on_error,
            )

            # Navigate to filing
            console.print("  [dim]Navigating to filing page...[/dim]")
            retry_on_error(
                lambda: court.navigate_to_filing(page),
                description="navigate to filing",
            )
            browser.screenshot("filing_page")
            check_page_state(page)

            # Enter case
            console.print("  [dim]Entering case number...[/dim]")
            retry_on_error(
                lambda: court.enter_case_number(page, self.filing.case.case_number),
                description="enter case number",
            )
            browser.screenshot("case_entered")
            check_page_state(page)

            # Select event
            console.print("  [dim]Selecting event type...[/dim]")
            retry_on_error(
                lambda: court.select_event(page, self.filing.event.code),
                description="select event",
            )
            browser.screenshot("event_selected")
            check_page_state(page)

            # Select filing party
            if self.filing.filing_party:
                console.print("  [dim]Selecting filing party...[/dim]")
                selected = court.select_parties(page, [self.filing.filing_party.party_name])
                if selected == 0:
                    console.print("  [yellow]⚠ Could not auto-select party — may need manual selection[/yellow]")
                browser.screenshot("party_selected")

            # Upload documents
            main_doc = self.filing.main_document
            if main_doc:
                console.print("  [dim]Uploading main document...[/dim]")
                retry_on_error(
                    lambda: court.upload_document(page, main_doc.file_path),
                    description="upload document",
                )
                browser.screenshot("document_uploaded")
                check_page_state(page)

            for att in self.filing.attachments:
                console.print(f"  [dim]Uploading attachment: {att.filename}...[/dim]")
                court.upload_attachment(page, att.file_path, att.description)

            # Related entry
            if self.filing.related_entry:
                console.print("  [dim]Selecting related docket entry...[/dim]")
                court.select_related_entry(
                    page, self.filing.related_entry.docket_number
                )

            # Docket text (required by most courts)
            docket_text = self.filing.docket_text or self.filing.event.description
            console.print("  [dim]Filling docket text...[/dim]")
            court.fill_docket_text(page, docket_text)

            # Brief notice (required for motions)
            if "motion" in self.filing.event.description.lower():
                court.fill_brief_notice(page, self.filing.event.description)

            # Fee status
            court.select_fee_status(page, "paid")

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

    def _offer_save_draft(self) -> None:
        """Offer to save the current filing as a draft."""
        if not self.filing:
            return

        try:
            if Confirm.ask("  Save as draft for later?", default=True):
                from ecfiler.filing.drafts import save_draft

                name = Prompt.ask(
                    "  Draft name",
                    default=f"{self.filing.court_id}_{self.filing.case.case_number}",
                )
                data = self.filing.model_dump(mode="json")
                path = save_draft(name, data)
                console.print(f"  [green]✓[/green] Draft saved: {path}")
                console.print(f"  [dim]Resume with: ecfiler drafts[/dim]")
        except Exception:
            pass  # Don't let draft save failure mask the original error
