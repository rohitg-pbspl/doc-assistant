from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class _NoteFields(BaseModel):
    # Strips before Field constraints run, so "  ab  " fails min_length=3.
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("tags", check_fields=False)
    @classmethod
    def normalize_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        return sorted({tag.lower() for tag in value if tag})


class NoteCreate(_NoteFields):
    title: str = Field(min_length=3, max_length=200)
    body: str = ""
    tags: list[str] = []


class NoteUpdate(_NoteFields):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    body: str | None = None
    tags: list[str] | None = None

    # Defaults are not validated, so this only fires on an explicit null.
    # Without it, {"title": null} would survive exclude_unset and blank the note.
    @field_validator("title", "body", "tags")
    @classmethod
    def reject_explicit_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("may be omitted but not null")
        return value


class NoteRead(BaseModel):
    # Lets FastAPI build the response straight from a Note ORM object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    body: str
    tags: list[str]
    created_at: datetime
