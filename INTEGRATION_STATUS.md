# MCIAS-Core — Isolated integration baseline

**Status: engineering integration in progress; NOT production-approved.**

This repository is independent from `overurdream-collab/test2`. Its `main` branch remains unchanged. All imported source is isolated on `integration/core-baseline`.

## Scope
1. INPUTS: six approved, complete and service-date-valid reference families.
2. CLAIMS: Excel claims-only import; exclude payment and summary sheets.
3. AUDIT: deterministic checks and evidence.
4. REVIEW: human decisions.
5. REPORT: four agreed indicators and claim-level traceability.

## Source provenance
Initial baseline copied from `overurdream-collab/test2` at `b69defa2f621458ef44d790b510840307a81009a`. Imported: `mcias/`, `alembic/`, `tests/`, `scripts/`, `deploy/`, runtime configuration, and CI workflows. This is a **baseline import, not proof of working end-to-end integration**. Additional feature PRs are not automatically incorporated.

## Local verification (isolated environment only)
Use a dedicated PostgreSQL database, distinct credentials and volumes, and test data only.

```bash
python -m pip install -e '.[test]'
alembic upgrade head
pytest -q
uvicorn mcias.app:app --host 127.0.0.1 --port 8000
```

**Do not run migrations against the original project's database.** No production data, automatic rejections, payments, or merge to main.

## Acceptance blockers
- Verify all imported files and dependencies, migrations and CI in this repository.
- Bring the eight INPUTS sections and import/add/edit UI from PR #25 only after tests.
- Enforce trusted claims worksheet classification before G4 stage/resume.
- Integrate G2 → G4 → six G3 references → G5 → Shared Audit → G6 → G7.
- Test Docker/PostgreSQL 16 and browser workflow end-to-end; record evidence.
- Preserve original `test2` entirely unchanged.

The integration branch is a **staging branch**, not a released application.

## Verified work in the independent repository (2026-10-22)
- Imported isolated baseline from original main with 283 tracked source/config/test/docs files; later restored 56 text documentation/evidence files needed for the acceptance pack.
- Original repository test2 remains untouched; MCIAS-Core main remains untouched.
- Independent CI revealed 343 unit tests passing, 19 skipped, and one missing acceptance-contract link; restored the missing source documentation.
- PG16 integration jobs passed on the initial import; this does **not** constitute complete end-to-end acceptance.
- Adopted the Pillow >=13,<14 dependency range from the existing security patch branch, pending exact-head CI verification.
- Added a fail-closed gate preventing unclassified Excel workbooks from entering G4 claim batches, with a regression test. **XLSX claim import remains BLOCKED** until an attested per-sheet CLAIMS/PAYMENT/SUMMARY classifier is implemented and tested. This is intentional and must not be represented as complete Excel support.
- Further integration of PR #25 inputs, Shared Audit, CAI-01, G6/G7 and full browser E2E remains OPEN. No production acceptance, no deployment, no merge.

## Independent verification and continuation — 2026-10-22
- Resumed from confirmed HEAD `c46e2554b071e95703e64f23b64e2c378972955a`; checked repository tree (339 tracked files), recent commits, and exact-SHA CI jobs before changing anything.
- Unit CI on that SHA: **344 passed, 19 skipped, 1 failed**. The single failing acceptance-pack test pointed to absent `GATE_STATUS.md` from policy links. G9 release-security failed on the same missing file. Restored the original file verbatim from `test2` main at `b69defa2f621458ef44d790b510840307a81009a` in commit `c3673e445393d0930dffd7c6af96400a2b4d1adb`.
- On the inspected SHA, PostgreSQL integration **PASS**, G9 PostgreSQL **PASS**, G8 **PASS**, Dependency Audit **PASS**. Enterprise browser-and-contracts job **FAIL**; detailed failure reason still requires confirmation. These are historical results on the inspected SHA, not fresh results for the restoration commit.
- Existing `Pillow>=13,<14` change, XLSX fail-closed gate, and regression test were already present; no duplication or conflicting edits made.
- Still blocked: attested per-sheet CLAIMS/PAYMENT/SUMMARY classification, full Excel import, eight INPUTS UI, six-reference checks, Shared Audit → G6 → G7, browser E2E and independent runtime acceptance. Fail-closed Excel protection is intentional, not complete import support.
- Neither `test2` nor `MCIAS-Core/main` has been modified; no merge or deployment.

## CAI-01 isolated preflight reuse — 2026-10-22
- Imported `mcias/claims_batch_preflight.py` unchanged from original PR #31 HEAD `bd2d1b0c92a5410466217802be936dd469b3b35f`, commit `b8a2b93c09c2308b010eaba43de147440d8cbbca`.
- Imported its synthetic contract tests `tests/test_cai01_inputs_first_source_contract.py`, commit `ba3c148d4097d736cbe5e7ab42cc7f0216f6f33d`.
- The preflight is read-only and checks explicit sheet scope, row identity, counts, duplicate locators, and normalization. It **does not attest sheet approval** or integrate with G4 persistence. The existing XLSX fail-closed G4 gate stays active; do not bypass it based on a caller-supplied sheet list.
- Earlier exact-SHA `2206a1aa3010` CI confirmed G1–G7, G8 and G9 success; Enterprise was still running when inspected. New preflight commits require their own CI confirmation.
- Remaining: independently approved worksheet classification, integration with G4, reference completeness at service date, Shared Audit, human review and G7 end-to-end browser acceptance.

## Worksheet scope contract — 2026-10-22
- Confirmed all four CI workflows **PASS** on previous SHA `eaefaea6d162eb4428e67a16a93f3cc7f0bda473` (G1–G7, G8, G9, Enterprise). This is not E2E acceptance.
- Added `mcias/claim_sheet_scope.py` in `8432a3a0583d0b5af0dd4724f1677a1cf274b3df` and seven synthetic contract tests in `f8832f588a196e64519aaee27e8f79fe4a8b3ebe`.
- Validator requires explicit per-sheet CLAIMS/PAYMENT/SUMMARY/OTHER labels, source SHA, extraction job ID, approver identity, full observed sheet coverage, and clean CAI-01 read-only preflight. Payment and summary rows are excluded from selected claims; malformed/missing scope fails closed.
- **Security boundary:** the validator does not prove the approver identity or authorization. A protected, auditable approval API and persistent attestation lifecycle are not implemented. Accordingly the XLSX G4 stage gate **remains closed**; no user-supplied manifest may bypass it. No claims totals are computed from unapproved sheets.
- CI for these two commits is pending verification; the earlier four-workflow green result belongs only to the prior SHA. No main merge, deployment, or original repository edits.

## G4 Excel approval and staging integration — 2026-10-22
- On SHA `c8229f836a1fa4c160ea73ae2321fec99b469b8e`, all four GitHub workflows (G1–G7, G8, G9, Enterprise) were observed PASS.
- `29fc3b1818d82549edaa373b34c4a2ba858f4e7c`: wired source-bound worksheet validation into G4 stage/preview/resume, preserving existing CSV behavior. Batch count and imported rows now include only explicitly approved CLAIMS worksheets; PAYMENT/SUMMARY excluded.
- `b13079288ddeee94cd703a4565bff18aea06a40e`: added tenant-scoped worksheet approval endpoint requiring both `claims.import` and `ingestion.review`, complete extraction, no quarantine, immutable approval once recorded, and append-only audit log event. This is a first integration, not independent security certification.
- `66d6b1d04ac138f232bfa7dd1643e253ec708de1`: updated prior fail-closed test expectation for the new approval requirement.
- `12fdc83d32149ffc231c57659ac83206bef3f142`: added synthetic G4 import regression: one claims row + payment + summary; asserts only the claims row is staged/imported. Test execution on the new HEAD is pending CI.
- No live production data, no deployment, no merge. Still open: cross-tenant/role approval API security tests, immutable approval storage hardening, reference completeness, Shared Audit integration, human review and final reports E2E.
