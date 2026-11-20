"""HTTP endpoints for the Member resource."""

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status, Request
from app.schemas.members import MemberInput, MemberResponse
from app.schemas.books import BookResponse
from app.services.interfaces import MemberServiceAbstraction
from app.exceptions import ResourceNotFoundError, DuplicateResourceError, BusinessRuleError
from app.auth import get_current_role, require_admin

router = APIRouter(
    prefix="/members",
    tags=["Members"],
    responses={401: {"description": "Unauthorized"}},
)

def get_member_service(request: Request) -> MemberServiceAbstraction:
    """Extract the active member service from application state."""
    return request.app.state.member_service

@router.get("", response_model=list[MemberResponse])
def list_members(
    service: MemberServiceAbstraction = Depends(get_member_service),
    role: str = Depends(get_current_role),
):
    return service.get_members()

@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    responses={404: {"description": "Not Found"}},
)
def get_member(
    member_id: int = Path(..., ge=1, le= 2147483647),  # Valid range for a 32-bit signed integer
    service: MemberServiceAbstraction = Depends(get_member_service),
    role: str = Depends(get_current_role),
):
    try:
        return service.get_member_by_id(member_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.get(
    "/{member_id}/books",
    response_model=list[BookResponse],
    responses={404: {"description": "Not Found"}},
)
def get_member_books(
    member_id: int = Path(..., ge=1, le= 2147483647),  # Valid range for a 32-bit signed integer
    service: MemberServiceAbstraction = Depends(get_member_service),
    role: str = Depends(get_current_role),
):
    try:
        return service.get_member_books(member_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post(
    "",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Forbidden"},
        409: {"description": "Conflict"},
    },
)
def create_member(
    data: MemberInput,
    service: MemberServiceAbstraction = Depends(get_member_service),
    role: str = Depends(require_admin),
):
    try:
        return service.create_member(data)
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        409: {"description": "Conflict"},
    },
)
def replace_member(
    member_id: int = Path(..., ge=1, le= 2147483647),  # Valid range for a 32-bit signed integer
    data: MemberInput = ...,
    service: MemberServiceAbstraction = Depends(get_member_service),
    role: str = Depends(require_admin),
):
    try:
        return service.replace_member(member_id, data)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        409: {"description": "Conflict"},
    },
)
def delete_member(
    member_id: int = Path(..., ge=1, le= 2147483647),  # Valid range for a 32-bit signed integer
    service: MemberServiceAbstraction = Depends(get_member_service),
    role: str = Depends(require_admin),
):
    try:
        service.delete_member(member_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BusinessRuleError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))