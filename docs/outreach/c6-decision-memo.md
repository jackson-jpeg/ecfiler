# C6 — What a "no" from each channel means (decision memo)

One page. The roadmap already assumes no federal filing API exists for anyone; none
of these answers can take away something we depend on. Each channel is an option, not
a dependency.

| Channel | Realistic bad outcome | What it changes | What it does NOT change |
|---|---|---|---|
| **Dev mailbox (C2)** | Silence, or "no plans to extend interfaces; no channel for input" | Nothing operational. Log it; it documents that we asked the right way. The PCL/auth APIs remain available regardless. | Read-side integration; Florida track; local-execution filing model |
| **EPA User Group (C3)** | Not selected (12 seats, strong applicant pool) | Lose a formal seat, keep the informal channels: public comment cycles, the dev list, and reapplication in the next cycle (membership caps at two consecutive terms, so seats rotate) | Everything else; apply again in 2 years |
| **Clerk inquiry (C5)** | "The court declines to opine" or a narrow reading of staff use | If *declines*: status quo — local rules still permit staff use of accounts under supervision; we simply lack a citable blessing. If *narrow/adverse in writing*: that's real — treat M.D. Fla. as a manual-filing district in the product, and do not send the same inquiry elsewhere until the framing is reworked with counsel. | Other districts (an M.D. Fla. answer binds only M.D. Fla.); the prepare-don't-submit hosted mode, which no reading touches |
| **White paper (C4)** | Ignored | Nothing. It exists, it's citable in future comment cycles and the EPA application, and requirements documents have long shelf lives inside procurement programs. | — |
| **Florida Authority (B3)** | Application rejected or scope restricted | Slower state track: cure the stated deficiency and reapply (restricted certifications are normal — several current vendors carry them). Worst case: Florida revenue deferred; federal prep product unaffected. | Federal track entirely |

## The one genuinely dangerous outcome

An **adverse written answer from a clerk or the AO that characterizes supervised
software-assisted filing as impermissible credential use.** That is why: (1) C5 is
framed around staff-operated, attorney-supervised tooling — a description that also
covers every big-firm docketing department in the country, making a blanket "no"
institutionally awkward; (2) nothing is sent without Jackson's approval; (3) we never
ask the AO that question at all (§4's core rule: position, don't petition).

## Standing decision rules

- One channel, one message, one follow-up (+3 weeks dev mailbox, +4 weeks clerk),
  then stop. Persistence reads as lobbying and creates a worse record than silence.
- Any written answer — good or bad — gets filed in `docs/outreach/replies/` verbatim
  and reflected in the contact tracker before anything else is sent anywhere.
- If two channels return adverse signals, pause all federal outreach and reassess
  with counsel before any third contact. Florida proceeds regardless.
