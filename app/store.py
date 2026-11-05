from itertools import count

from app.schemas import NoteCreate, NoteRead, NoteUpdate


class NoteStore:
    """In-memory notes. Per process: lost on restart, not shared between workers."""

    def __init__(self) -> None:
        self._notes: dict[int, NoteRead] = {}
        self._ids = count(1)

    def create(self, data: NoteCreate) -> NoteRead:
        note = NoteRead(id=next(self._ids), **data.model_dump())
        self._notes[note.id] = note
        return note

    def list(self, limit: int) -> list[NoteRead]:
        return list(self._notes.values())[:limit]

    def get(self, note_id: int) -> NoteRead | None:
        return self._notes.get(note_id)

    def update(self, note_id: int, data: NoteUpdate) -> NoteRead | None:
        note = self._notes.get(note_id)
        if note is None:
            return None
        updated = note.model_copy(update=data.model_dump(exclude_unset=True))
        self._notes[note_id] = updated
        return updated

    def delete(self, note_id: int) -> bool:
        return self._notes.pop(note_id, None) is not None


store = NoteStore()
