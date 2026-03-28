from fastapi import HTTPException


class NotFoundError(HTTPException):
    def __init__(self, resource: str, id: str):
        super().__init__(status_code=404, detail=f"{resource} '{id}' not found")


class ConflictError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=409, detail=detail)


class UpstreamError(HTTPException):
    def __init__(self, service: str, detail: str):
        super().__init__(status_code=502, detail=f"{service} error: {detail}")


class ApprovalRequired(HTTPException):
    def __init__(self, action: str):
        super().__init__(
            status_code=403,
            detail=f"Approval required before executing: {action}",
        )
