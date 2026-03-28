from fastapi import APIRouter, HTTPException

from app.schemas.approval import ApprovalResolveRequest
from app.services import approval_service

router = APIRouter()


@router.post("/{approval_id}/approve")
async def approve(approval_id: str, body: ApprovalResolveRequest = ApprovalResolveRequest()):
    approval = approval_service.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval["status"] != "pending":
        raise HTTPException(status_code=409, detail=f"Approval already {approval['status']}")
    return await approval_service.resolve(approval_id, "approved", body.reason)


@router.post("/{approval_id}/deny")
async def deny(approval_id: str, body: ApprovalResolveRequest = ApprovalResolveRequest()):
    approval = approval_service.get_approval(approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval["status"] != "pending":
        raise HTTPException(status_code=409, detail=f"Approval already {approval['status']}")
    return await approval_service.resolve(approval_id, "denied", body.reason)


@router.get("/session/{session_id}")
def list_pending(session_id: str):
    return approval_service.get_pending(session_id)
