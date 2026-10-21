"""Synthetic INPUTS-FIRST completeness tests."""
from datetime import date
from types import SimpleNamespace
from mcias.inputs_first_certificate import FAMILIES, inspect_reference_evidence

CLAIM=SimpleNamespace(id="synthetic-claim",service_date=date(2026,10,20))

def approved():
    return {name:{"reference_id":name+"-v1","version":1,"source":"synthetic",
                  "approved":True,"coverage_complete":True,
                  "effective_from":"2026-01-01","effective_until":"2027-01-01"} for name in FAMILIES}

def test_six_approved_valid_families_ready():
    r=inspect_reference_evidence(CLAIM,approved())
    assert r["status"]=="READY_FOR_ANALYSIS"
    assert len(r["references"])==6
    assert all(x["status"]=="VERIFIED" for x in r["references"])

def test_missing_beneficiary_does_not_imply_ineligible():
    e=approved()
    del e["beneficiaries_eligibility"]
    r=inspect_reference_evidence(CLAIM,e)
    assert r["status"]=="HOLD_INPUTS"
    assert "eligibility" not in r
    assert r["references"][0]["status"]=="HOLD"

def test_expired_contract_blocks():
    e=approved()
    e["contracts_coverages"]["effective_until"]="2026-10-20"
    assert inspect_reference_evidence(CLAIM,e)["status"]=="HOLD_INPUTS"

def test_incomplete_history_blocks():
    e=approved()
    e["historical_claims_records"]["coverage_complete"]=False
    r=inspect_reference_evidence(CLAIM,e)
    assert r["status"]=="HOLD_INPUTS"
    assert "coverage" in r["references"][-1]["missing"]

def test_unapproved_policy_blocks():
    e=approved()
    e["policies_approvals"]["approved"]=False
    assert inspect_reference_evidence(CLAIM,e)["status"]=="HOLD_INPUTS"

def test_malformed_date_never_passes_temporal_validation():
    e=approved()
    e["contracts_coverages"]["effective_from"]="2026-99-99"
    result=inspect_reference_evidence(CLAIM,e)
    assert result["status"]=="HOLD_INPUTS"
    assert "valid_at_service_date" in result["references"][1]["missing"]

def test_reversed_period_never_passes():
    e=approved()
    e["provider_tariffs_prices"]["effective_from"]="2027-01-01"
    e["provider_tariffs_prices"]["effective_until"]="2026-01-01"
    assert inspect_reference_evidence(CLAIM,e)["status"]=="HOLD_INPUTS"
