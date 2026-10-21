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
