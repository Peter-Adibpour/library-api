"""HTTP endpoints for the Member resource."""

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from app.schemas.members import MemberInput, MemberResponse
from app.services.interfaces import MemberServiceAbstraction

router = APIRouter(prefix="/members", tags=["Members"])

def get_member_service(request: Request) -> MemberServiceAbstraction:
    """Extract the active member service from application state."""
    return request.app.state.member_service

@router.get("", response_model=list[MemberResponse])
def list_members(service: MemberServiceAbstraction = Depends(get_member_service)):
    return service.get_members()

@router.get("/{member_id}", response_model=MemberResponse)
def get_member(member_id: int, service: MemberServiceAbstraction = Depends(get_member_service)):
    try:
        return service.get_member_by_id(member_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
def create_member(data: MemberInput, service: MemberServiceAbstraction = Depends(get_member_service)):
    try:
        return service.create_member(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.put("/{member_id}", response_model=MemberResponse)
def replace_member(member_id: int, data: MemberInput, service: MemberServiceAbstraction = Depends(get_member_service)):
    try:
        return service.replace_member(member_id, data)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(member_id: int, service: MemberServiceAbstraction = Depends(get_member_service)):
    try:
        service.delete_member(member_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        if "associated books" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))