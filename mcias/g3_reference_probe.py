"""Read-only G3 reference probe grounded in tenant-scoped database records.

No client attestation can turn missing institutional references into approval.
"""
from sqlalchemy import select
from mcias.models_reference import BeneficiaryEnrollment, ContractVersion, ProviderTariff
from mcias.inputs_first_certificate import FAMILIES

def inspect_g3_claim(db, claim):
    at=claim.service_date
    enrollments=db.scalars(select(BeneficiaryEnrollment).where(
        BeneficiaryEnrollment.organization_id==claim.organization_id,
        BeneficiaryEnrollment.beneficiary_token==claim.beneficiary_token,
        BeneficiaryEnrollment.effective_from<=at,
        BeneficiaryEnrollment.effective_until>at)).all()
    contracts=db.scalars(select(ContractVersion).where(
        ContractVersion.organization_id==claim.organization_id,
        ContractVersion.provider_code==claim.provider_code,
        ContractVersion.status=="approved",
        ContractVersion.effective_from<=at,
        ContractVersion.effective_until>at)).all()
    contract=contracts[0] if len(contracts)==1 else None
    tariffs=db.scalars(select(ProviderTariff).where(
        ProviderTariff.contract_id==contract.id,
        ProviderTariff.service_code==claim.service_code,
        ProviderTariff.currency==claim.currency)).all() if contract else []
    def found(family, rows, label, version=None, period=None):
        if len(rows)!=1:
            return {"family":family,"status":"HOLD","missing":[
                "ambiguous_reference" if rows else "reference_or_coverage_not_proven"],
                "reference_id":None,"version":None,"source":"tenant_scoped_G3"}
        item=rows[0]
        return {"family":family,"status":"PARTIAL",
                "reference_id":item.id,"version":version if version is not None else 1,
                "source":"tenant_scoped_G3","effective_from":period[0].isoformat() if period else None,
                "effective_until":period[1].isoformat() if period else None,
                "missing":["institutional_coverage_completeness_not_attested"]}
    items=[
        found(FAMILIES[0],enrollments,"enrollment",period=(enrollments[0].effective_from,enrollments[0].effective_until) if len(enrollments)==1 else None),
        found(FAMILIES[1],contracts,"contract",version=contract.version if contract else None,
              period=(contract.effective_from,contract.effective_until) if contract else None),
        found(FAMILIES[2],tariffs,"tariff"),
    ]
    items += [{"family":family,"status":"HOLD","reference_id":None,
               "version":None,"source":None,"missing":["trusted_approved_temporal_reference_not_integrated"]}
              for family in FAMILIES[3:]]
    return {"claim_id":claim.id,"service_date":at.isoformat(),
            "status":"HOLD_INPUTS","references":items,
            "semantics":"DATABASE_EVIDENCE_ONLY_NO_INELIGIBILITY_OR_FINANCIAL_DECISION"}
