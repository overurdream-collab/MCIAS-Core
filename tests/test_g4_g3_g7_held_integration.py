"""Synthetic G4 -> G3 -> G7 integration: missing references never create payable.

This is an isolated SQLite regression, NOT PG16 acceptance or a full G5/G6 run.
"""
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from mcias.models import Base
from mcias.models_claims import ClaimEntry
from mcias.claim_batches import stage, resume
from mcias.g3_reference_probe import inspect_g3_claim
from mcias.reporting_g7 import freeze_batch, fingerprint
from tests.test_g4_batches import _fixture

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
