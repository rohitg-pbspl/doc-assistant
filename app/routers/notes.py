from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_current_user
from app.schemas import NoteCreate, NoteRead, NoteUpdate
from app.store import store

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_note(data: NoteCreate) -> NoteRead:
    return store.create(data)


@router.get("")
def list_notes(limit: Annotated[int, Query(ge=1, le=100)] = 20) -> list[NoteRead]:
    return store.list(limit)


@router.get("/{note_id}")
def get_note(note_id: int) -> NoteRead:
    note = store.get(note_id)
    if note is None:
        raise _not_found()
    return note


@router.patch("/{note_id}")
def update_note(note_id: int, data: NoteUpdate) -> NoteRead:
    note = store.update(note_id, data)
    if note is None:
        raise _not_found()
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: int) -> None:
    if not store.delete(note_id):
        raise _not_found()


def _not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
