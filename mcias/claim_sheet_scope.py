"""Validate explicit per-worksheet claim scope before any G4 import.

No automatic classification by column shape or worksheet position.
Approval must be tied to a specific source SHA and extraction job.
"""
from mcias.claims_batch_preflight import inspect_extracted_records

VALID_KINDS = {"CLAIMS", "PAYMENT", "SUMMARY", "OTHER"}

def validate_sheet_scope(document, job, records):
    if not document.filename.lower().endswith((".xlsx", ".xlsm", ".xls")):
        return list(records)
    scope = job.manifest.get("claim_sheet_attestation")
    if not isinstance(scope, dict) or scope.get("source_sha256") != document.sha256 or scope.get("job_id") != job.id:
        raise ValueError("trusted claim sheet attestation required")
    sheets = scope.get("sheets")
    if not isinstance(sheets, dict) or not sheets:
        raise ValueError("complete sheet classification required")
    if not isinstance(scope.get("approved_by"), str) or not scope["approved_by"].strip():
        raise ValueError("sheet classification approval identity required")
    if any(not isinstance(r.locator, dict) for r in records):
        raise ValueError("invalid Excel source locator")
    observed = {r.locator.get("index") for r in records}
    if any(r.locator.get("kind") != "sheet" or type(r.locator.get("index")) is not int for r in records):
        raise ValueError("invalid Excel source locator")
    if any(type(k) is not str or not k.isdecimal() or str(int(k)) != k for k in sheets):
        raise ValueError("invalid worksheet index")
    mapped = {int(k): v for k, v in sheets.items()}
    if set(mapped) != observed or any(v not in VALID_KINDS for v in mapped.values()):
        raise ValueError("unclassified or invalid worksheet")
    selected = {index for index, kind in mapped.items() if kind == "CLAIMS"}
    if not selected:
        raise ValueError("no approved claims worksheets")
    result = inspect_extracted_records(records, claim_sheet_indices=selected, expected_records=len(records))
    if result["status"] != "READY_FOR_G4":
        raise ValueError("source preflight blocked: " + ",".join(result["reason_codes"]))
    return [r for r in records if r.locator["index"] in selected]
