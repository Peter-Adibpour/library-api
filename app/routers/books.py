"""HTTP endpoints for the Book resource."""

from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from app.schemas.books import BookInput, BookResponse
from app.services.interfaces import BookServiceAbstraction

router = APIRouter(prefix="/books", tags=["Books"])

def get_book_service(request: Request) -> BookServiceAbstraction:
    """Extract the active book service from application state."""
    return request.app.state.book_service

@router.get("", response_model=list[BookResponse])
def list_books(service: BookServiceAbstraction = Depends(get_book_service)):
    return service.get_books()

@router.get("/{book_id}", response_model=BookResponse)
def get_book(book_id: int, service: BookServiceAbstraction = Depends(get_book_service)):
    try:
        return service.get_book_by_id(book_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(data: BookInput, service: BookServiceAbstraction = Depends(get_book_service)):
    try:
        return service.create_book(data)
    except ValueError as e:
        if "member does not exist" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.put("/{book_id}", response_model=BookResponse)
def replace_book(book_id: int, data: BookInput, service: BookServiceAbstraction = Depends(get_book_service)):
    try:
        return service.replace_book(book_id, data)
    except ValueError as e:
        if "book not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "member does not exist" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, service: BookServiceAbstraction = Depends(get_book_service)):
    try:
        service.delete_book(book_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))