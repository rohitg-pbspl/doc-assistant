from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import SessionDep
from app.dependencies import get_current_user
from app.models import Note
from app.schemas import NoteCreate, NoteRead, NoteUpdate

router = APIRouter(
    prefix="/notes",
    tags=["notes"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_note(data: NoteCreate, session: SessionDep) -> NoteRead:
    note = Note(**data.model_dump())
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


@router.get("")
async def list_notes(
    session: SessionDep, limit: Annotated[int, Query(ge=1, le=100)] = 20
) -> list[NoteRead]:
    notes = await session.scalars(select(Note).order_by(Note.id).limit(limit))
    return notes.all()


@router.get("/{note_id}")
async def get_note(note_id: int, session: SessionDep) -> NoteRead:
    return await _get_or_404(session, note_id)


@router.patch("/{note_id}")
async def update_note(note_id: int, data: NoteUpdate, session: SessionDep) -> NoteRead:
    note = await _get_or_404(session, note_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(note, field, value)
    await session.commit()
    await session.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(note_id: int, session: SessionDep) -> None:
    note = await _get_or_404(session, note_id)
    await session.delete(note)
    await session.commit()


async def _get_or_404(session: AsyncSession, note_id: int) -> Note:
    note = await session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    return note
