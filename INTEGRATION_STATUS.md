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

## Approval segregation and attestation-change regression — 2026-10-22
- Verified all four workflows G1–G7/G8/G9/Enterprise **PASS** on SHA `db8e6621c9a0a3155c6ed97f5620b34f2bbae80e`.
- `4236e80cf18730466726e777343ddf12f1f530e7`: worksheet approval now checks the original `source_ingested` audit event and refuses same-actor approval or absent provenance. This enforces distinct uploader/reviewer identities in addition to both permissions. It does not replace formal independent security review.
- `03441dc6b0c1843596d9550f4955379760154def`: synthetic test confirms changing approved sheet labels after G4 staging blocks resume instead of silently importing another sheet.
- CI on these new commits is not yet verified. Approval audit-log and manifest persistence still need concurrent PostgreSQL verification, and full six-reference audit → Shared Audit → human review → reporting E2E remains open. No merge or deployment.

## INPUTS-FIRST six-family certificate — 2026-10-22
- Verified all four CI workflows PASS at previous SHA `5b0c4ae89cebe7711d66db5288e542adc582c0af`.
- Added `mcias/inputs_first_certificate.py` at `2a208035eba89a3df71208ad622973f586b7f42d` and five synthetic tests at `bd71e5d21daf90bd0b0dc608649b9f3e3ef01332`.
- The read-only certificate enumerates all six reference families, provenance, approval, coverage and temporal validity at service date. Missing beneficiary evidence yields HOLD_INPUTS, **never ineligibility**.
- IMPORTANT: input evidence is caller-provided and this module is NOT a trusted G3 reference resolver, not a policy authorization, not wired into G5, and not a production-ready integration. Full DB-backed verification and end-to-end audit remain open.
- CI for these new commits has not yet been confirmed. No main merge, original repo edits, or deployment.

## DB-grounded G3 probe — 2026-10-22
- On `5c1199b75eb214da2ea5b4b18f0cdaed0168a4b9`, G1–G7, G8 and G9 were confirmed PASS; Enterprise was still in progress at the initial check.
- `a06f7abae02a4ef4c0fb515de45cb25ea86fc4d2` introduces read-only tenant-scoped G3 probe for active beneficiary enrollment, approved contract and matching tariff at service date; it never treats record presence as proof that institutional coverage is complete.
- `3ec39eebf8a03253188020f8855ba61cfc8c52e0` adds a synthetic SQLite tenant-isolation test with different tariff amounts for two organizations, plus explicit HOLD for the remaining three unintegrated families.
- This probe always returns HOLD_INPUTS, is not yet G5-wired, and does not assert ineligibility. No six-reference completeness attestation, Shared Audit, or E2E approval yet. New commit CI unverified.

## Verified resumption and gap register — 2026-10-22
- Resumption base HEAD: `c316e7638b2b7da7b7def947a1a0fdf0abf93642`. Confirmed four GitHub Actions workflows all completed **success** on this exact SHA: G1–G7 run 39691593253, G8 39691593197, G9 39691593184, Enterprise 39691593123. Draft PR #1 remains open and unmerged.
- Existing completed work was inspected and **not duplicated**: Excel worksheet approval and G4 selection, six-family advisory certificate, read-only DB-backed G3 probe, and existing synthetic tests.
- New `70e3ec39bcf02fb60fe0be5f5713f25f98c387b6`: exposed `GET /api/v1/claims/entries/{claim_id}/inputs-first` with existing claims.read authorization, organization-scoped ClaimEntry lookup, and the existing read-only G3 probe. Does not grant eligibility or financial authorization.
- New `4286f275144b453ba59585e50b8eee6124dd1826`: test of the endpoint with a synthetic imported claim, all six families HOLD without references, and cross-tenant 404.
- These new commits require their **own** CI results before any PASS claim. No main merge, original test2 changes, deployment, or production data.
- Remaining: independently verifiable six-family approved/complete temporal references; trusted coverage attestation; G5 and Shared Audit integration; G6 human decisions; G7 final four KPIs and five classifications; PostgreSQL 16 end-to-end and browser acceptance.

## CI inspection and temporal validity hardening — 2026-10-22
- Verified latest resumption HEAD `2c11815e4e0b86aca3bdb8cb26c360642524f289`; G1–G7, G8, G9 were **success**, Enterprise still running at check time.
- Investigated earlier G1–G7 failure on `4286f275144b453ba59585e50b8eee6124dd1826`: postgres-integration and dependency-audit passed; unit job failed solely at `tests/test_operational_controls.py::test_middleware_returns_429_retry_after_and_ignores_forwarded_headers` (observed 200 instead of expected 429), with 370 passed, 19 skipped. A subsequent run on `2c11815e4` passed. No test weakening or speculative rate-limiter patch.
- `59051f73c7633ce6ff573183c9b6e40aba04c39a`: corrected temporal certificate to parse ISO dates rather than lexicographically compare arbitrary strings.
- `1613763830e2cb16641e7b3463a56ec48d2e331d`: added malformed-date and reversed-date synthetic regressions.
- CI for these newest commits not yet confirmed. Full DB-backed six-family attestation and G5→G6→G7 integration still blocked; no merge or deployment.

## G4 completed-batch scope integrity — 2026-10-22
- Resumed at HEAD `82b3b96d691f18789d876055a61dd3933ba8d8f9`. G1–G7/G8/G9 were in progress on that exact SHA at the initial check. Earlier SHA `1613763830e2cb16641e7b3463a56ec48d2e331d` had G1–G7/G8/G9 PASS, Enterprise still in progress.
- Inspected G4 source and found an early `imported` return in `resume()` that bypassed worksheet attestation/source revalidation for completed batches. This could conceal a later altered scope on an idempotent resume.
- `2d3f07796e027d89e078708b684f82407dae6d3f` adds source SHA and sheet scope revalidation before completed-batch return.
- `22f870167f65df9a92883f34dfc92b9819f0b443` adds a synthetic regression: repeated resume succeeds while unchanged, then rejects a changed sheet classification without adding entries.
- This detects tampering on resume, but **does not establish database-enforced immutability** of JSON manifest or cryptographically signed attestation. Dedicated PostgreSQL concurrency and API role tests still required.
- New HEAD CI is pending; no merge, deployment or original repo mutation.

## Resumption: worksheet locator malformed-input hardening — 2026-10-22
- Inspected branch `integration/core-baseline` at `c905736c6d415d9b74a826c306be2de57c601bbd`. All four workflows **PASS on that exact SHA**: G1–G7 #39692599315, G8 #39692599341, G9 #39692599307, Enterprise #39692599291. Draft PR #1 remains unmerged.
- Reused existing worksheet scope validator and preflight; no duplicate parser or importer. Found a malformed `locator=None` would cause an uncaught AttributeError during sheet-index collection rather than a controlled validation rejection.
- `8ebb9c3fdc299b438482ce0cd519b88280e4d622`: reject non-dictionary locators with a controlled ValueError before accessing fields.
- `566b81efa5b34885b3088bc6d760b744f85fe655`: add two synthetic regressions for malformed locator and payment/summary-only workbook. These newest tests have not yet been independently confirmed PASS.
- Remaining known issues: full workbook sheet inventory (including sheets with zero extracted records) not yet attested; durable DB-enforced approval immutability; six trusted reference families; G5→Shared Audit→G6→G7 end-to-end, PG16/browser acceptance. No main merge or deployment.

## Complete worksheet inventory — 2026-10-22
- Resumed from `b8cf4b7f7900ef9f806eb1652144f19f98700b7f`; PR #1 remained open/draft/unmerged. At the initial inspection, its four workflows were still running; prior `c905736c6d415d9b74a826c306be2de57c601bbd` had four successful workflows.
- Inspected the actual G2 parser, extraction schema, manifest, G4 scope validator, and their tests before editing.
- `26754713baadfb0cf71ed4627f90081f2307c012`: added optional worksheet inventory to G2 extraction schema.
- `c66791f8f2318b45d50173a4d159728d511e25fd`: captures every workbook worksheet index and name, including empty sheets.
- `cf6145b5190518cd371efd80949a62aa82495bd5`: records inventory in G2 manifest.
- `cff60d6186506443c4bd99a29948e39060e1e697`: G4 checks attestation against the full workbook inventory when available, not only observed claim rows; legacy G2 manifests without inventory continue existing observed-row validation.
- `ad5d151a389e97f8cbb0967b5bf4c0a6ef18b7bf`: synthetic tests for mandatory classification of an empty sheet and rejection of duplicate inventory indexes.
- These newest commits are **not yet verified green** on CI. Workbook sheet names are captured as metadata, but per-claim row locator still contains sheet index, not name; evidence schema and institutional attestation remain incomplete. No merge or deployment.

## G2 source row provenance — 2026-10-22
- Resumed from `af91946216cef82cc6349375d32b2971ba8a6a21`, PR #1 open/draft/unmerged. On that SHA all four CI workflows were still queued/in progress at inspection; no invented green claim.
- Inspected `ingestion/orchestrator.py`, `ingestion/provenance.py`, `models_ingestion.py` and G4 scope before edits. Reused existing row locator JSON without adding conflicting schema migration.
- `9c209cced77a72e7570e4ee5d455dd3080b8fe15`: new Excel extracted rows carry `sheet_name` and `source_sha256` in G2 locator; other source formats unchanged.
- `f1b62010f72b1a1a6ad28d58e3fc57ab6d01606f`: G4 rejects a supplied row sheet name or SHA that disagrees with the workbook inventory and document fingerprint.
- `793d78b5e70b4e838a5bc54478e9048432958758`: two synthetic mismatch regression tests.
- Compatibility caveat: older extracted rows lacking the new optional locator keys remain supported. The row does not yet persist its approval acceptance state; attestation still resides in mutable JSON and needs independent PostgreSQL hardening. New CI not yet verified. No merge/deployment.

## Integration acceptance pivot — 2026-10-22
- Verified `ffd892addd22a6b0b2fbdec7e5392071599024c3` has **all four CI workflows successful on the same SHA** (G1–G7, G8, G9, Enterprise).
- Inspected existing `audit_service.py` and `reporting_g7.py`. G5 already requires a verified institutional policy grant, while G7 can safely freeze a held/unapproved imported batch without fabricating financial approvals. These engines are reused, not duplicated.
- `dac51e3cc2b79275d950a24adf77e28ab14be303` added a synthetic integration regression for G4 import → G3 HOLD_INPUTS → G7 frozen held-only report; `c031a16ba9a7d37c1d10ac68f47dae0144d086ce` made its fixture self-contained.
- Expected assertions: one imported claim, six reference statuses, no approved claims, zero payable, held claim, stable report fingerprint. This is **not** a full G2 Excel→G5→Shared Audit→G6→G7 acceptance test, and is not PostgreSQL 16 proof.
- CI for new integration test is pending verification. No merges or deployment.
