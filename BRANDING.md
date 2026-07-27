# ECFiler Brand Guide

## Positioning

**One-liner:** Open-source filing preparation and locally-controlled automation for Federal CM/ECF courts.

**Tagline:** File with confidence. File with code you can read.

**Elevator pitch:** ECFiler is an open-source tool that prepares, validates, and stages filings for federal court CM/ECF systems — and, from your own machine, automates the mechanical filing steps under your control. It uses AI to match your filing to the right event code, scans for redaction issues, validates your documents, and never submits without your explicit approval. Your court credentials never leave your machine. Unlike $500/month proprietary tools, ECFiler's code is fully auditable — because when your bar license is on the line, you should be able to see exactly what's happening.

## Voice & Tone

- **Professional, not corporate.** Write like a senior associate explaining something to a colleague, not a marketing team writing ad copy.
- **Precise.** Lawyers notice imprecise language. Say exactly what ECFiler does and doesn't do.
- **Understated.** No exclamation marks, no "revolutionary", no "game-changing". Let the product speak.
- **Honest about limitations.** If something doesn't work yet, say so. Credibility > hype.

### Do say:
- "ECFiler validates your PDF against CM/ECF requirements before filing."
- "You must type CONFIRM before any document is submitted."
- "Event code suggestions are AI-assisted — always verify before filing."

### Don't say:
- "ECFiler automatically files your documents!" (misleading — attorney must confirm)
- "Your credentials, encrypted on our servers" (we do not have them — that is the point)
- "Automated CM/ECF submission" as a hosted feature (the hosted product stages; the human files)
- "Never worry about filing again!" (they should still review)
- "AI-powered legal assistant" (sounds like UPL)

## Key Messages

### For solo practitioners / small firms:
"Stop paying $500/month for filing software. ECFiler is free, open-source, and does the same job — with more transparency."

### For large firms / IT departments:
"Self-hosted, auditable, and extensible. ECFiler integrates into your existing workflow without vendor lock-in. Every filing is logged, every action has a screenshot."

### For legal tech community:
"An open-source CM/ECF filing-preparation tool. Built on Playwright + Claude API. 207 federal courts. Contributions welcome."

### For bar associations / ethics committees:
"ECFiler is a mechanical filing assistant, not a legal advisor. It validates documents and automates mechanical form steps locally, under attorney supervision, with credentials that never leave the attorney's machine. The attorney reviews and confirms every filing. Every filing action is recorded in an append-only, hash-chained attestation log."

## Differentiation

| Feature | ECFiler (Free) | PacerPro ($$$) | ECFX ($$$) |
|---------|---------------|----------------|------------|
| Open source | ✓ | ✗ | ✗ |
| Auditable code | ✓ | ✗ | ✗ |
| AI event code matching | ✓ | ✗ | ✗ |
| Redaction scanning | ✓ | ✗ | Limited |
| Attorney confirmation required | ✓ | N/A | N/A |
| Self-hosted option | ✓ | ✗ | ✗ |
| All 207 federal courts | ✓ | ✓ | ✓ |
| Local attorney-controlled filing automation | ✓ | ✗ (read-only) | ✓ |
| Zero server credential custody | ✓ | ✓ | ? |
| Cost | Free | ~$200-500/mo | ~$300-600/mo |

## Target Audiences (Priority Order)

1. **Solo practitioners & small firms (1-10 attorneys)** — Price-sensitive, tech-comfortable, file frequently. This is the beachhead market.
2. **Legal aid organizations & pro bono attorneys** — Budget-constrained, mission-driven. Great for word-of-mouth and credibility.
3. **Mid-size firms (10-50 attorneys)** — Need team features (ECFiler Pro). Higher revenue per customer.
4. **Legal tech developers** — Build on top of ECFiler. Grow the ecosystem.
5. **Large firms (50+ attorneys)** — Enterprise features, support contracts. Longest sales cycle but highest revenue.

## Naming

- **ECFiler** — the product. Always capitalized as "ECFiler", not "ecfiler" or "EC Filer" in marketing copy. (Lowercase `ecfiler` is acceptable in code and CLI contexts.)
- **ECFiler Pro** — the paid SaaS tier (future).
- **ECFiler Enterprise** — managed service for large firms (future).

## Logo Concept

The logo should evoke:
- A courthouse column (tradition, authority)
- A file/document icon (what we do)
- Clean geometric lines (precision, reliability)

Color palette:
- Primary: Deep navy (#1B2A4A) — authority, trust
- Accent: Gold/amber (#C4952A) — justice scales, legal tradition
- Background: White/light gray — clean, professional
- Success: Forest green (#2D7D46)
- Error: Deep red (#B22234)
