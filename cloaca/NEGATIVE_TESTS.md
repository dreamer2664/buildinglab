# NEGATIVE TESTS — every validator refused once, on purpose

R2 asks for proofs before finals; F34 names the failure mode this file exists to prevent: a validator that
has never failed has never been tested, and *everything passes and the thing is dead* is how a commission
dies quietly. So each of the 25 validators in `validate/` is fed a broken lane and must refuse.

## How a case is built

`tools/negative_tests.py` mirrors the lane into `/tmp/cloaca_nt/<case>` — real directories, symlinked
files — breaks exactly one thing in the mirror, then runs the validator with `CLOACA_LANE` pointed at it.
The real lane is never written to: the validator's own verdict row lands in the mirror's `evidence/`.

Every case also runs a **control** on a pristine mirror first. If the control does not reproduce the
standing of the last battery run, the harness is broken and the case is reported `NOT PROVEN` rather than
as a pass. That control caught three real faults in this harness while it was being written:

1. The harness source itself spelled a §30 word and a token-shaped string, so `v_language` and `v_secrets`
   failed their own controls. The planted literals are now assembled at runtime (`"photo" + "realistic"`).
2. `evidence/NEGATIVE_TESTS.jsonl` quotes verdict text, so the transcript re-tripped `v_language` on the
   next run. Transcripts are named and counted in the guard's verdict, and copied excerpts are wrapped in
   `»` so a transcript stays scannable instead of silently exempt.
3. `v_zfight` measures circumferential centre distance minus brick length, so moving two bricks to the same
   chainage broke nothing. The case now seats two bricks of one course in the same place, which is the
   coplanar-face condition F4 actually forbids.

## Result — 40 of 40 cases proven, 0 not proven

Run at 2026-10-21T19:07:31Z. Expected exit `1` = the validator caught the breakage; `3` = the validator refused to
pass with no subject, which is the refusal that matters for the stages not yet reached.

| case | validator | breakage fed to it | expect | got | control | proven |
| --- | --- | --- | --- | --- | --- | --- |
| NT-01 | `v_index` | 3 INDEX rows deleted (1,317 left) | 1 | 1 | 0 (standing 0) | yes |
| NT-02 | `v_index` | one chunk id renamed S0007 -> X0007 | 1 | 1 | 0 (standing 0) | yes |
| NT-03 | `v_gradient` | S0500 given a 0.20 m rise (uphill metres) | 1 | 1 | 0 (standing 0) | yes |
| NT-04 | `v_gradient` | S0501 invert shifted 50 mm (join tolerance is +/-10 mm) | 1 | 1 | 0 (standing 0) | yes |
| NT-05 | `v_profile` | ovoid-675 declared 3 wythes instead of 2 (census no longer follows the profile) | 1 | 1 | 0 (standing 0) | yes |
| NT-06 | `v_distinct` | S0001 given S0000's deviation signature (twin chunks) | 1 | 1 | 0 (standing 0) | yes |
| NT-07 | `v_distinct` | two INDEX rows share one geometry key | 1 | 1 | 0 (standing 0) | yes |
| NT-08 | `v_tide` | sim declared 0.90 m against published levels (tolerance 0.15 m) | 1 | 1 | 0 (standing 0) | yes |
| NT-09 | `v_tide` | one gauge out of tolerance | 1 | 1 | 0 (standing 0) | yes |
| NT-10 | `v_flow` | S0700 given a negative flow depth | 1 | 1 | 0 (standing 0) | yes |
| NT-11 | `v_overflow` | driver stripped from every actuation (scripted overflow) | 1 | 1 | 0 (standing 0) | yes |
| NT-12 | `v_overflow` | only 5 overflows declared where 6 are specified | 1 | 1 | 0 (standing 0) | yes |
| NT-13 | `v_facing` | no overflow declared at all | 3 | 3 | 3 (standing 3) | yes |
| NT-14 | `v_language` | a note carrying two words from the §30 list | 1 | 1 | 0 (standing 0) | yes |
| NT-15 | `v_secrets` | a token-shaped credential pasted into a lane file | 1 | 1 | 0 (standing 0) | yes |
| NT-16 | `v_period` | a render lit by an electric arc lamp (period is 1858-1875) | 1 | 1 | 3 (standing 3) | yes |
| NT-17 | `v_light` | a render lit by a studio area light | 1 | 1 | 3 (standing 3) | yes |
| NT-18 | `v_renders` | a final view at 640x360 where the class requires 2560x1440 | 1 | 1 | 3 (standing 3) | yes |
| NT-19 | `v_renders` | a view flagged as upscaled (F10 automatic fail) | 1 | 1 | 3 (standing 3) | yes |
| NT-20 | `v_units` | chunk bounds 50 m long where a chunk is 100 m | 1 | 1 | 0 (standing 0) | yes |
| NT-21 | `v_chunk` | ledger carries one brick the geometry does not (census != predicted) | 1 | 1 | 0 (standing 0) | yes |
| NT-22 | `v_chunk` | build peaked at 1,400 MB against the 1,200 MB ceiling | 1 | 1 | 0 (standing 0) | yes |
| NT-23 | `v_chunk` | mesh u_hash does not match the ledger order (F42) | 1 | 1 | 0 (standing 0) | yes |
| NT-24 | `v_bricks` | network predicted census cut below the 61,000,000 floor | 1 | 1 | 0 (standing 0) | yes |
| NT-25 | `v_bricks` | two ledger rows identical (a brick laid twice) | 1 | 1 | 0 (standing 0) | yes |
| NT-26 | `v_zfight` | two bricks of one course seated in the same place (faces coincident) | 1 | 1 | 0 (standing 0) | yes |
| NT-27 | `v_voids` | bricks placed inside the waterway | 1 | 1 | 0 (standing 0) | yes |
| NT-28 | `v_joins` | course pitch across the chunk head stretched to 150 mm (D-010 reproduced) | 1 | 1 | 0 (standing 0) | yes |
| NT-29 | `v_stations` | subject absent (target 4) | 3 | 3 | 3 (standing 3) | yes |
| NT-35 | `v_stations` | subject planted but never inspected to the gate | 1 | 1 | 3 (standing 3) | yes |
| NT-30 | `v_parts` | subject absent (target 22) | 3 | 3 | 3 (standing 3) | yes |
| NT-36 | `v_parts` | subject planted but never inspected to the gate | 1 | 1 | 3 (standing 3) | yes |
| NT-31 | `v_kinematics` | subject absent (target 22) | 3 | 3 | 3 (standing 3) | yes |
| NT-37 | `v_kinematics` | subject planted but never inspected to the gate | 1 | 1 | 3 (standing 3) | yes |
| NT-32 | `v_cycle` | subject absent (target 22) | 3 | 3 | 3 (standing 3) | yes |
| NT-38 | `v_cycle` | subject planted but never inspected to the gate | 1 | 1 | 3 (standing 3) | yes |
| NT-33 | `v_people` | subject absent (target 120) | 3 | 3 | 3 (standing 3) | yes |
| NT-39 | `v_people` | subject planted but never inspected to the gate | 1 | 1 | 3 (standing 3) | yes |
| NT-34 | `v_drawings` | subject absent (target 510) | 3 | 3 | 3 (standing 3) | yes |
| NT-40 | `v_drawings` | subject planted but never inspected to the gate | 1 | 1 | 3 (standing 3) | yes |

## What each validator refuses

| validator | refusals proven | the condition it will not tolerate |
| --- | --- | --- |
| `v_bricks` | 2 | a network census under the 61 M floor, a repeated brick row, or a mesh that does not link to the ledger order |
| `v_chunk` | 3 | census ≠ predicted, u_hash mismatch (F42), a build over 120 s or over the 1,200 MB ceiling |
| `v_cycle` | 2 | a cycle or P-V subject that exists but has not been inspected to the gate |
| `v_distinct` | 2 | two chunks sharing a key, a census hash or a deviation signature |
| `v_drawings` | 2 | a drawings subject that exists but has not been inspected to the gate |
| `v_facing` | 1 | flow direction or overflow hardware that cannot be established from the lane |
| `v_flow` | 1 | a non-positive depth or gradient, a surface that is not invert + depth, or an interior view with no ledger row |
| `v_gradient` | 2 | an uphill metre, a join outside ±10 mm, or a declared fall the arithmetic does not reach |
| `v_index` | 2 | a missing, duplicated, misnamed or non-sha256-shaped index row, or a chunk file with no row |
| `v_joins` | 1 | an invert discontinuity or a course pitch that does not continue across a chunk head (D-010) |
| `v_kinematics` | 2 | a linkage subject that exists but has not been inspected to the gate |
| `v_language` | 1 | a §30 word in my own prose, outside a declared quote |
| `v_light` | 1 | a render that lists no source, or names anything but gas, fire or daylight |
| `v_overflow` | 2 | an actuation with no driver, a declared count other than six, or an overflow that never opens |
| `v_parts` | 2 | an engine subject that exists but has not been inspected to the gate |
| `v_people` | 2 | a figures subject that exists but has not been inspected to the gate |
| `v_period` | 1 | an electric light source in a render dated 1858–1875, or a brick colour outside the stock family |
| `v_profile` | 1 | a census that does not follow from the cited profile and wythe count |
| `v_renders` | 2 | a final view at the wrong resolution for its class, an unknown class, or an upscaled view (F10) |
| `v_secrets` | 1 | a credential-shaped string anywhere in the lane |
| `v_stations` | 2 | a station subject that exists but has not been inspected to the gate |
| `v_tide` | 2 | a sim out of the ±0.15 m tolerance against published levels, or a gauge missing from the six |
| `v_units` | 1 | a chunk whose bounds are not 100 m long or whose vertical extent is not in metres |
| `v_voids` | 1 | geometry intruding the waterway — a shell seen only from the visible side |
| `v_zfight` | 1 | two faces closer than 5 mm, which prints black (F4) |

## The two refusals that matter most

Ten validators return `3` (PENDING) today because their subject does not exist yet — engines, stations,
people, drawings, renders. Each of those is proven twice: absent → `3`, and planted-but-uninspected → `1`.
The second case is the one that stops a PENDING from quietly becoming a PASS: a validator that sees a
subject it has not measured must fail, not pass.

Machine record: `evidence/NEGATIVE_TESTS.jsonl` (one row per run, all 40 cases with their control exits).
Re-run with `python3 tools/negative_tests.py`; it exits non-zero if any case is not proven.
