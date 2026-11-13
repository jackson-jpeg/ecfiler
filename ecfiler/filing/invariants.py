"""Hard invariants enforced immediately before browser submission.

Silently retargeting a filing to a different court than the one staged is
the worst failure mode this product has — it is precisely the error ECFiler
exists to prevent. These checks run after every override and lookup has been
applied, on the exact objects the submit step is about to use, and any
mismatch aborts the run. They are deliberately dumb string comparisons: no
normalization beyond a trailing-slash strip, no fuzzy matching, no fallback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ecfiler.config import FilingEnvironment
    from ecfiler.courts.base import BaseCourt
    from ecfiler.filing.models import Filing


class CourtSubstitutionError(Exception):
    """The court about to be filed in is not the court that was staged/selected."""


def enforce_court_invariants(
    filing: "Filing", court: "BaseCourt", env: "FilingEnvironment"
) -> None:
    """Abort unless the resolved court is exactly the intended one.

    Checks, in order:
    1. The resolved court instance answers to the filing's court_id.
    2. The court's PACER environment matches the run's (QA runs file only in
       QA courts, production runs only in production courts).
    3. If ECFILER_ECF_URL is set, it must EQUAL the court's own ECF URL —
       it is a confirmation, never a substitution. (Exception: a localhost
       mock court URL, which by definition reaches no real court.)
    4. If the filing was staged, the staged court_id and ECF URL must match
       the resolved court byte for byte.

    Raises:
        CourtSubstitutionError: on any mismatch.
    """
    profile = court.profile

    if profile.court_id != filing.court_id:
        raise CourtSubstitutionError(
            f"Resolved court '{profile.court_id}' does not match the filing's "
            f"court '{filing.court_id}' — aborting."
        )

    # Staged provenance is checked before the environment so the message
    # names the court the attorney actually attested to — the most useful
    # thing to see when a run aborts.
    staged = filing.staged
    if staged is not None:
        if staged.court_id != filing.court_id:
            raise CourtSubstitutionError(
                f"This filing was staged for court '{staged.court_id}' but now "
                f"names '{filing.court_id}' — the court changed after the "
                f"attorney attested. Aborting."
            )
        if staged.court_id != profile.court_id:
            raise CourtSubstitutionError(
                f"This filing was staged for court '{staged.court_id}' but "
                f"resolved to '{profile.court_id}' — aborting."
            )
        if staged.ecf_url.rstrip("/") != profile.ecf_url.rstrip("/"):
            raise CourtSubstitutionError(
                f"Staged ECF URL ({staged.ecf_url}) does not match the "
                f"resolved court's ECF URL ({profile.ecf_url}) for "
                f"'{profile.court_id}' — the endpoint changed after staging. "
                f"Aborting."
            )
        if staged.environment != profile.environment:
            raise CourtSubstitutionError(
                f"This filing was staged in the {staged.environment} "
                f"environment but court '{profile.court_id}' is "
                f"{profile.environment} — aborting."
            )

    run_env = "qa" if env.use_qa else "production"
    if profile.environment != run_env:
        raise CourtSubstitutionError(
            f"Court '{profile.court_id}' belongs to the {profile.environment} "
            f"PACER environment but this run is {run_env} — aborting."
        )

    if env.ecf_url_override:
        override = env.ecf_url_override.rstrip("/")
        actual = profile.ecf_url.rstrip("/")
        is_mock = override.startswith("http://localhost") or override.startswith(
            "http://127.0.0.1"
        )
        if override != actual and not is_mock:
            raise CourtSubstitutionError(
                f"ECFILER_ECF_URL ({override}) does not match court "
                f"'{profile.court_id}' ({actual}). The URL override confirms "
                f"the target; it never retargets a filing — aborting."
            )
