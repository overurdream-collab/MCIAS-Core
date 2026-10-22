"""Tenant-isolated G3 probe regression tests, no invented reference approvals."""
from datetime import date
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from mcias.models import Base, Organization, User
from mcias.models_reference import ContractVersion, ProviderTariff, BeneficiaryCategory, BeneficiaryEnrollment
from mcias.g3_reference_probe import inspect_g3_claim

def test_probe_only_sees_own_approved_temporal_references():
    engine=create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        own=Organization(name="own-probe")
        other=Organization(name="other-probe")
        db.add_all([own,other]);db.flush()
        owncat=BeneficiaryCategory(organization_id=own.id,code="A",description="A")
        othercat=BeneficiaryCategory(organization_id=other.id,code="A",description="A")
        db.add_all([owncat,othercat]);db.flush()
        for org,cat in ((own,owncat),(other,othercat)):
            db.add(BeneficiaryEnrollment(organization_id=org.id,beneficiary_token="B",
                category_id=cat.id,effective_from=date(2026,1,1),effective_until=date(2027,1,1)))
        owncontract=ContractVersion(organization_id=own.id,provider_code="P",version=1,
            effective_from=date(2026,1,1),effective_until=date(2027,1,1),status="approved")
        othercontract=ContractVersion(organization_id=other.id,provider_code="P",version=1,
            effective_from=date(2026,1,1),effective_until=date(2027,1,1),status="approved")
        db.add_all([owncontract,othercontract]);db.flush()
        db.add_all([ProviderTariff(contract_id=owncontract.id,service_code="S",
            amount=Decimal("10"),currency="YER"),
            ProviderTariff(contract_id=othercontract.id,service_code="S",
            amount=Decimal("100"),currency="YER")])
        db.commit()
        from types import SimpleNamespace
        claim=SimpleNamespace(id="synthetic",organization_id=own.id,
            beneficiary_token="B",provider_code="P",service_code="S",
            currency="YER",service_date=date(2026,10,20))
        result=inspect_g3_claim(db,claim)
        assert result["status"]=="HOLD_INPUTS"
        assert len(result["references"])==6
        assert result["references"][0]["status"]=="PARTIAL"
        assert result["references"][1]["reference_id"]==owncontract.id
        assert result["references"][2]["status"]=="PARTIAL"
        assert all(x["status"]=="HOLD" for x in result["references"][3:])
        claim.organization_id="unknown"
        missing=inspect_g3_claim(db,claim)
        assert all(x["status"]=="HOLD" for x in missing["references"][:3])
    engine.dispose()
