"""Read-only, fail-closed six-family reference evidence certificate.

Caller evidence is NOT trusted authorization or an eligibility verdict.
"""
from datetime import date as Date

FAMILIES=("beneficiaries_eligibility","contracts_coverages","provider_tariffs_prices",
          "policies_approvals","limits_ceilings","historical_claims_records")

def inspect_reference_evidence(claim, evidence):
    if not isinstance(evidence,dict):
        raise ValueError("reference evidence mapping required")
    results=[]
    for family in FAMILIES:
        item=evidence.get(family)
        if not isinstance(item,dict):
            results.append({"family":family,"status":"HOLD","missing":["reference evidence"]})
            continue
        date=claim.service_date.isoformat()
        start,end=item.get("effective_from"),item.get("effective_until")
        try:
            temporal=(type(start) is str and type(end) is str
                      and Date.fromisoformat(start)<=claim.service_date<Date.fromisoformat(end))
        except ValueError:
            temporal=False
        checks={"approval":item.get("approved") is True,
                "coverage":item.get("coverage_complete") is True,
                "valid_at_service_date":temporal,
                "reference_id":bool(item.get("reference_id")),
                "version":item.get("version") is not None,
                "source":bool(item.get("source"))}
        missing=[key for key,passed in checks.items() if not passed]
        results.append({"family":family,"status":"VERIFIED" if not missing else "HOLD",
                        "reference_id":item.get("reference_id"),"version":item.get("version"),
                        "effective_from":start,"effective_until":end,"source":item.get("source"),
                        "coverage_complete":checks["coverage"],"missing":missing})
    return {"claim_id":claim.id,"service_date":claim.service_date.isoformat(),
            "status":"READY_FOR_ANALYSIS" if all(x["status"]=="VERIFIED" for x in results) else "HOLD_INPUTS",
            "references":results,"semantics":"ADVISORY_ONLY_NOT_AUTHORIZATION_OR_ELIGIBILITY"}
