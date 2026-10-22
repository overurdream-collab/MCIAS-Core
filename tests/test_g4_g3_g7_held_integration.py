"""Synthetic G4 -> G3 -> G7 integration: missing references never create payable.

This is an isolated SQLite regression, NOT PG16 acceptance or a full G5/G6 run.
"""
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from mcias.models import Base, Organization, User, SourceFile
from mcias.models_claims import ClaimEntry
from mcias.models_ingestion import IngestionDocument, IngestionJob, ExtractedSourceRecord
from mcias.claim_batches import stage, resume
from mcias.g3_reference_probe import inspect_g3_claim
from mcias.reporting_g7 import freeze_batch, fingerprint
from mcias.audit_service import run_audit
from mcias.audit_engine import PolicyBlocked
from mcias.models_audit import AuditSnapshot
import pytest
def _fixture(db):
    org=Organization(name="synthetic-integration")
    actor=User(username="synthetic-integration-user",password_hash="fixture")
    db.add_all([org,actor]);db.flush()
    actor.organization_id=org.id
    source=SourceFile(sha256="a"*64,original_filename="claims.csv",storage_key="synthetic")
    db.add(source);db.flush()
    doc=IngestionDocument(organization_id=org.id,source_id=source.id,
        sha256="a"*64,filename="claims.csv",status="extracted")
    db.add(doc);db.flush()
    job=IngestionJob(organization_id=org.id,document_id=doc.id,status="extracted",
        manifest={"complete":True})
    db.add(job);db.flush()
    row=ExtractedSourceRecord(job_id=job.id,
        locator={"kind":"row","index":1,"row":2},
        values={"claim_reference":"SYN-1","beneficiary_token":"synthetic-token",
                "provider_code":"P","service_code":"S","service_date":"2026-10-20",
                "claimed_amount":"100.0000","currency":"YER"},confidence=100)
    db.add(row);db.commit()
    return org,actor,doc,row


def test_imported_claim_with_missing_references_freezes_held_report():
    engine=create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine,expire_on_commit=False) as db:
        org,actor,doc,row=_fixture(db)
        batch=stage(db,actor,doc.id)
        imported=resume(db,actor,batch.id)
        assert imported["status"]=="imported"
        claims=db.scalars(select(ClaimEntry).where(ClaimEntry.batch_id==batch.id)).all()
        assert len(claims)==1
        certificate=inspect_g3_claim(db,claims[0])
        assert certificate["status"]=="HOLD_INPUTS"
        assert len(certificate["references"])==6
        assert all(x["status"]=="HOLD" for x in certificate["references"])
        # G5 must not accept a financial execution without trusted policy authorization.
        with pytest.raises(PolicyBlocked, match="verified institutional policy authorization required"):
            run_audit(db, actor, claims[0].id, None)
        assert db.scalar(select(AuditSnapshot.id).where(AuditSnapshot.claim_id==claims[0].id)) is None
        dataset,summary=freeze_batch(batch,claims,[],[],[])
        assert summary["total_claims"]==1
        totals=summary["by_currency"]["YER"]
        assert totals["approved_count"]==0
        assert totals["held_count"]==1
        assert totals["payable"]=="0"
        assert dataset["rows"][0]["state"]=="held"
        assert dataset["rows"][0]["hold_reason"]=="awaiting_verified_approval"
        assert len(fingerprint(dataset,summary))==64
    engine.dispose()
