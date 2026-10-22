"""Tenant-isolated G4 batch and claim API."""
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session
from mcias.app import get_db
from mcias.auth import resolve_user
from mcias.tenant import require_organization
from mcias.models_claims import ClaimBatch, ClaimEntry, ClaimAttachment
from mcias.models_ingestion import IngestionDocument, IngestionJob, ExtractedSourceRecord, QuarantineItem
from mcias.models import AuditLog
from mcias.claim_sheet_scope import validate_sheet_scope
from mcias.claim_batches import BatchConflict, stage, preview, resume, attach

router=APIRouter(prefix="/api/v1/claims",tags=["claims"])

def _actor(db,authorization,permission):
    user,_=resolve_user(db,authorization)
    if not user.organization_id:
        raise HTTPException(403,"organization required")
    require_organization(db,user,user.organization_id,permission)
    return user

def _run(db,fn):
    try:
        return fn()
    except BatchConflict as exc:
        db.rollback()
        raise HTTPException(409,str(exc)) from exc
    except __import__("sqlalchemy").exc.IntegrityError as exc:
        db.rollback()
        raise HTTPException(409,"claim integrity constraint") from exc

@router.post("/batches/from-document/{document_id}",status_code=201)
def create_batch(document_id: str,authorization: str | None=Header(default=None),
                 db:Session=Depends(get_db)):
    actor=_actor(db,authorization,"claims.import")
    batch=_run(db,lambda:stage(db,actor,document_id))
    return {"id":batch.id,"status":batch.status,"record_count":batch.record_count}

@router.get("/batches/{batch_id}/preview")
def batch_preview(batch_id:str,limit:int=Query(default=100,ge=1,le=500),
                  offset:int=Query(default=0,ge=0),
                  authorization:str|None=Header(default=None),db:Session=Depends(get_db)):
    actor=_actor(db,authorization,"claims.read")
    return _run(db,lambda:preview(db,actor,batch_id,limit,offset))

@router.post("/batches/{batch_id}/resume")
def resume_batch(batch_id:str,chunk_size:int=Query(default=100,ge=1,le=1000),
                 authorization:str|None=Header(default=None),db:Session=Depends(get_db)):
    actor=_actor(db,authorization,"claims.import")
    return _run(db,lambda:resume(db,actor,batch_id,chunk_size))

@router.get("/batches/{batch_id}")
def get_batch(batch_id:str,authorization:str|None=Header(default=None),
              db:Session=Depends(get_db)):
    actor=_actor(db,authorization,"claims.read")
    batch=db.get(ClaimBatch,batch_id)
    if batch is None or batch.organization_id!=actor.organization_id:
        raise HTTPException(404,"batch not found")
    return {"id":batch.id,"status":batch.status,"record_count":batch.record_count,
            "imported_count":batch.imported_count,"source_sha256":batch.source_sha256}

@router.get("/batches/{batch_id}/entries")
def batch_entries(batch_id:str,limit:int=Query(default=100,ge=1,le=500),
                  offset:int=Query(default=0,ge=0),
                  authorization:str|None=Header(default=None),db:Session=Depends(get_db)):
    actor=_actor(db,authorization,"claims.read")
    batch=db.get(ClaimBatch,batch_id)
    if batch is None or batch.organization_id!=actor.organization_id:
        raise HTTPException(404,"batch not found")
    entries=db.scalars(select(ClaimEntry).where(ClaimEntry.batch_id==batch.id,
        ClaimEntry.organization_id==actor.organization_id).order_by(ClaimEntry.id)
        .offset(offset).limit(limit)).all()
    return {"batch_id":batch.id,"entries":[{"id":c.id,"claim_reference":c.claim_reference,
        "source_locator":c.source_locator,"claimed_amount":str(c.claimed_amount),
        "currency":c.currency,"service_date":c.service_date.isoformat()} for c in entries]}

@router.post("/entries/{claim_id}/attachments/{document_id}",status_code=201)
def link_attachment(claim_id:str,document_id:str,authorization:str|None=Header(default=None),
                    db:Session=Depends(get_db)):
    actor=_actor(db,authorization,"claims.import")
    item=_run(db,lambda:attach(db,actor,claim_id,document_id))
    return {"id":item.id,"claim_id":item.claim_id,"document_sha256":item.document_sha256}

class WorksheetApproval(BaseModel):
    sheets: dict[str, str] = Field(min_length=1, max_length=50)
    rationale: str = Field(min_length=10, max_length=1000)

@router.post("/documents/{document_id}/approve-worksheets")
def approve_worksheets(document_id: str, payload: WorksheetApproval,
                       authorization: str | None=Header(default=None),
                       db: Session=Depends(get_db)):
    actor=_actor(db,authorization,"claims.import")
    from mcias.tenant import require_organization
    require_organization(db,actor,actor.organization_id,"ingestion.review")
    doc=db.get(IngestionDocument,document_id)
    if doc is None or doc.organization_id!=actor.organization_id:
        raise HTTPException(404,"document not found")
    if not doc.filename.lower().endswith((".xlsx",".xlsm",".xls")) or doc.status!="extracted":
        raise HTTPException(409,"extracted Excel document required")
    job=db.scalar(select(IngestionJob).where(IngestionJob.document_id==doc.id,
        IngestionJob.organization_id==actor.organization_id).order_by(IngestionJob.created_at.desc()).with_for_update())
    if job is None or job.status!="extracted" or not job.manifest.get("complete"):
        raise HTTPException(409,"extraction not complete")
    if db.scalar(select(QuarantineItem.id).where(QuarantineItem.job_id==job.id)):
        raise HTTPException(409,"source quarantine unresolved")
    if db.scalar(select(ClaimBatch.id).where(ClaimBatch.ingestion_document_id==doc.id,
        ClaimBatch.organization_id==actor.organization_id)):
        raise HTTPException(409,"source already staged; approval immutable")
    if job.manifest.get("claim_sheet_attestation"):
        raise HTTPException(409,"worksheet approval already exists")
    source_event=db.scalar(select(AuditLog).where(AuditLog.action=="source_ingested",
        AuditLog.resource_type=="ingestion_document",AuditLog.resource_id==doc.id)
        .order_by(AuditLog.id.desc()))
    if source_event is None or source_event.actor_id==actor.id:
        raise HTTPException(409,"independent worksheet reviewer required")
    records=db.scalars(select(ExtractedSourceRecord).where(ExtractedSourceRecord.job_id==job.id)).all()
    attestation={"source_sha256":doc.sha256,"job_id":job.id,
                 "approved_by":actor.id,"sheets":payload.sheets,"rationale":payload.rationale}
    job.manifest={**job.manifest,"claim_sheet_attestation":attestation}
    try:
        approved=validate_sheet_scope(doc,job,records)
    except ValueError as exc:
        db.rollback()
        raise HTTPException(409,str(exc)) from exc
    db.add(AuditLog(actor_id=actor.id,action="claim_worksheets_approved",
        resource_type="ingestion_document",resource_id=doc.id,
        details={"sha256":doc.sha256,"job_id":job.id,"sheets":payload.sheets,
                 "rationale":payload.rationale,"claims_count":len(approved)}))
    db.commit()
    return {"document_id":doc.id,"job_id":job.id,"approved_claim_rows":len(approved),
            "status":"APPROVED_FOR_G4_STAGING"}

@router.get("/entries/{claim_id}/inputs-first")
def claim_inputs_first(claim_id: str, authorization: str | None=Header(default=None),
                       db: Session=Depends(get_db)):
    """Read-only DB-grounded G3 probe; HOLD is not an eligibility decision."""
    actor=_actor(db,authorization,"claims.read")
    claim=db.scalar(select(ClaimEntry).where(
        ClaimEntry.id==claim_id,ClaimEntry.organization_id==actor.organization_id))
    if claim is None:
        raise HTTPException(404,"claim not found")
    from mcias.g3_reference_probe import inspect_g3_claim
    return inspect_g3_claim(db,claim)
