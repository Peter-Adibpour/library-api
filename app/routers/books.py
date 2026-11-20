"""HTTP endpoints for the Book resource."""

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status, Request
from app.schemas.books import BookInput, BookResponse
from app.services.interfaces import BookServiceAbstraction
from app.exceptions import ResourceNotFoundError, DuplicateResourceError
from app.auth import get_current_role, require_admin

router = APIRouter(
    prefix="/books",
    tags=["Books"],
    responses={401: {"description": "Unauthorized"}},
)

def get_book_service(request: Request) -> BookServiceAbstraction:
    """Extract the active book service from application state."""
    return request.app.state.book_service

@router.get("", response_model=list[BookResponse])
def list_books(
    service: BookServiceAbstraction = Depends(get_book_service),
    role: str = Depends(get_current_role),
):
    return service.get_books()

@router.get(
    "/{book_id}",
    response_model=BookResponse,
    responses={404: {"description": "Not Found"}},
)
def get_book(
    book_id: int = Path(..., ge=1, le=2147483647),  # Valid range for a 32-bit signed integer
    service: BookServiceAbstraction = Depends(get_book_service),
    role: str = Depends(get_current_role),
):
    try:
        return service.get_book_by_id(book_id)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post(
    "",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Associated member not found"},
        409: {"description": "Duplicate resource"},
    },
)
def create_book(
    data: BookInput,
    service: BookServiceAbstraction = Depends(get_book_service),
    role: str = Depends(require_admin),
):
    try:
        return service.create_book(data)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.put(
    "/{book_id}",
    response_model=BookResponse,
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
        409: {"description": "Conflict"},
    },
)
def replace_book(
    book_id: int = Path(..., ge=1, le=2147483647),  # Valid range for a 32-bit signed integer
    data: BookInput = ...,
    service: BookServiceAbstraction = Depends(get_book_service),
    role: str = Depends(require_admin),
):
    try:
        return service.replace_book(book_id, data)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except DuplicateResourceError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete(
    "/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {"description": "Forbidden"},
        404: {"description": "Not Found"},
    },
)
def delete_book(
    book_id: int = Path(..., ge=1, le=2147483647),  # Valid range for a 32-bit signed integer
    service: BookServiceAbstraction = Depends(get_book_service),
    role: str = Depends(require_admin),
):
    try:
        service.delete_book(book_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ResourceNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))