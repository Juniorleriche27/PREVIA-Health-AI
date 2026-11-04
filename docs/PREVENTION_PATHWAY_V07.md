# PREVIA Health AI — Module 07: Synthetic Prevention Pathway

## Purpose

The Future Health Digital Innovation Challenge's **Precision Prevention and Screening** track calls for solutions that support earlier, safer action. PREVIA v0.7 adds a reproducible proof-of-concept **screening-to-review workflow**. It is a **software demonstration** based on **fictitious profiles and workflow statuses**. No patient, hospital, practice or appointment is represented.

Official challenge: https://hack2skill.com/event/futurehealthchallenge/

WHO HEARTS technical reference: https://www.who.int/publications/i/item/9789240001367/
WHO HEARTS team-based care: https://www.who.int/publications/i/item/WHO-NMH-NVI-18-4
WHO HEARTS implementation guide: https://www.who.int/publications/i/item/WHO-NMH-NVI-18-14

## Architecture

- Next.js page: `frontend/app/pathways/page.tsx` at `/pathways`
- FastAPI router: `backend/app/pathways.py`
- API: `POST /api/v1/pathways/simulate`
- Existing synthetic population generator: `backend/app/population.py`
- Existing selectable demonstration strategies: `backend/app/prioritization.py`
- No persistent database or external messaging integration; every request replays a deterministic synthetic scenario.

## Reference example — 240 fictitious profiles, 45 simulated slots, Togo, seed 2026

- 45 synthetic IDs selected by the previously implemented algorithm.
- Pre-populated fictional stage counts: 45 identified, 38 invited, 30 engaged, 24 offered, 18 booked, 12 attended, 6 reviewed.
- The initial funnel ratios (85%, 67%, 54%, 40%, 27%, 14%) are **invented demonstration constants**, applied through integer truncation. They are not empirical uptake probabilities.
- Initial stage distribution is assigned in sorted fictional-ID order. It is deliberately not a calibrated demographic, epidemiologic or behavioral simulation.

### Supported transitions

| Current stage | Allowed next action | New stage |
| --- | --- | --- |
| Identified | invite | Invited |
| Invited | acknowledge; decline | Engaged; Declined |
| Engaged | offer_screening; decline | Offered; Declined |
| Offered | book; decline | Booked; Declined |
| Booked | attend; decline | Attended; Declined |
| Attended | review | Reviewed |
| Declined | reopen | Invited |
| Reviewed | no further event | Reviewed |

Invalid transitions and actions referencing a non-selected synthetic ID are rejected with HTTP 422. Reopen retains the most advanced past milestone for historical funnel accounting. Every state is reconstructed on each request from the seed and the optional list of actions supplied by the browser; no records are saved server-side.

## KPI definitions (all **synthetic**)

- **Selected N:** number of fictitious IDs allocated under a demonstration strategy.
- **Milestone N:** number of selected IDs that have reached a given stage at least once (even when subsequently declined).
- **Milestone share:** number reaching stage / selected N × 100.
- **Conditional stage conversion:** number reaching stage / number reaching prior stage × 100.
- **Simulated attendance share:** IDs with `attended` as highest stage / selected N × 100.
- **Simulated review-stage share:** IDs with `reviewed` as highest stage / selected N × 100. **Not** a measure of delivered clinical care.
- **Demonstration sector gap:** highest minus lowest fake review-stage share among demo sectors with selected IDs, in percentage points. **Not** a fairness measure for any real population.
- **Awaiting action:** selected minus currently reviewed minus currently declined.

## Safety and data integrity

- Only invented `SYN-0001` identifiers, controlled transitions and aggregate parameters are accepted. Personal names, emails, phone numbers and notes are rejected by strict API validation.
- No users are contacted; no visits are booked or attended; no professional medical review is performed.
- No user-provided medical records are retained. The client holds its local event history in browser component state while the page is open; refresh clears it.
- The WHO 2019 reference table supplies an educational chart-bin value, not an individualized diagnosis, validated clinical prediction or clinical triage rule.
- No medication, care urgency, screening interval or referral is prescribed by this module. Decisions require qualified clinicians and local clinical protocols.
- The v0.6 WHO text-layer check passed all 700 digitized cells, **not** a visual sign-off of every source cell; v0.6 NHANES input completeness does **not** establish 10-year event prediction accuracy.

## Test coverage

The new test suite covers the 240/45 reference cohort, three allocation rules, transition integrity, decline/reopen behavior, illegal actions, consent, extra patient-like fields, invalid IDs, small/large capacity, fixed seeds, WHO source, JSON report contract and statelessness. Tests and Next.js production build are available from `scripts/verify_v07.ps1`.

## What remains outside the scope of v0.7

Clinical co-design and approvals, independent real outcome validation, patient authentication and authorization, informed consent processes, interoperability with actual health records, scheduling systems, clinical safety monitoring, and outcomes studies.
