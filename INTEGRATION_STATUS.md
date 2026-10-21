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
