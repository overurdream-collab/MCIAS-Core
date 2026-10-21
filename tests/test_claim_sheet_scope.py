"""Synthetic worksheet-scope contract tests. No financial decisions."""
from types import SimpleNamespace
import pytest
from mcias.claim_sheet_scope import validate_sheet_scope

def fixture(sheets=None, sha="a"*64, job_sha=None):
    doc = SimpleNamespace(filename="claims.xlsx", sha256=sha)
    job = SimpleNamespace(id="job-1", manifest={"claim_sheet_attestation": {
        "source_sha256": job_sha or sha, "job_id":"job-1", "approved_by":"reviewer-1",
        "sheets": sheets if sheets is not None else {"1":"CLAIMS","2":"PAYMENT","3":"SUMMARY"}
    }})
    vals = {"claim_reference":"C1","beneficiary_token":"B","provider_code":"P",
            "service_code":"S","service_date":"2026-10-20","claimed_amount":"10.0000","currency":"YER"}
    records = [SimpleNamespace(id=f"r{i}", locator={"kind":"sheet","index":i,"row":2},
                               values=vals if i==1 else {"total":"100"}) for i in (1,2,3)]
    return doc,job,records

def test_only_approved_claim_sheet_selected():
    doc,job,records=fixture()
    assert [r.id for r in validate_sheet_scope(doc,job,records)]==["r1"]

def test_missing_attestation_blocks():
    doc,job,records=fixture()
    job.manifest={}
    with pytest.raises(ValueError,match="attestation"):
        validate_sheet_scope(doc,job,records)

def test_wrong_sha_blocks():
    doc,job,records=fixture(job_sha="b"*64)
    with pytest.raises(ValueError,match="attestation"):
        validate_sheet_scope(doc,job,records)

def test_unclassified_sheet_blocks():
    doc,job,records=fixture({"1":"CLAIMS","2":"PAYMENT"})
    with pytest.raises(ValueError,match="unclassified"):
        validate_sheet_scope(doc,job,records)

def test_payment_mislabeled_claims_blocks_invalid_row():
    doc,job,records=fixture({"1":"CLAIMS","2":"CLAIMS","3":"SUMMARY"})
    with pytest.raises(ValueError,match="preflight blocked"):
        validate_sheet_scope(doc,job,records)

def test_missing_approver_blocks():
    doc,job,records=fixture()
    job.manifest["claim_sheet_attestation"]["approved_by"]=""
    with pytest.raises(ValueError,match="approval identity"):
        validate_sheet_scope(doc,job,records)

def test_non_excel_keeps_existing_rows():
    doc,job,records=fixture()
    doc.filename="claims.csv"
    assert validate_sheet_scope(doc,job,records)==records
