import pytest
from httpx import AsyncClient

MISSING_ID = 999_999


# --- health and auth ---


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_missing_user_header_is_rejected(client: AsyncClient) -> None:
    del client.headers["X-User"]

    response = await client.get("/notes")

    assert response.status_code == 401


@pytest.mark.parametrize("user", ["", "   "])
async def test_blank_user_header_is_rejected(client: AsyncClient, user: str) -> None:
    response = await client.get("/notes", headers={"X-User": user})

    assert response.status_code == 401


# --- create ---


async def test_create_note(client: AsyncClient) -> None:
    response = await client.post("/notes", json={"title": "First note", "body": "hello"})

    assert response.status_code == 201
    note = response.json()
    assert note["id"] > 0
    assert note["title"] == "First note"
    assert note["body"] == "hello"
    assert note["tags"] == []
    assert note["created_at"]


async def test_create_normalizes_tags(client: AsyncClient) -> None:
    note = await _create_note(client, tags=["B", "a", "b", ""])

    assert note["tags"] == ["a", "b"]


async def test_create_strips_title_whitespace(client: AsyncClient) -> None:
    note = await _create_note(client, title="  Padded  ")

    assert note["title"] == "Padded"


@pytest.mark.parametrize(
    "payload",
    [
        {},  # title required
        {"title": "ab"},  # too short
        {"title": "  ab  "},  # too short once stripped
        {"title": "x" * 201},  # too long
        {"title": "Valid", "tags": "not-a-list"},
    ],
)
async def test_create_rejects_invalid_payload(client: AsyncClient, payload: dict) -> None:
    response = await client.post("/notes", json=payload)

    assert response.status_code == 422


# --- read ---


async def test_get_note(client: AsyncClient) -> None:
    created = await _create_note(client)

    response = await client.get(f"/notes/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


async def test_get_missing_note_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"/notes/{MISSING_ID}")

    assert response.status_code == 404


async def test_list_notes_in_id_order(client: AsyncClient) -> None:
    first = await _create_note(client, title="Note one")
    second = await _create_note(client, title="Note two")

    response = await client.get("/notes")

    assert response.status_code == 200
    assert [n["id"] for n in response.json()] == [first["id"], second["id"]]


async def test_list_respects_limit(client: AsyncClient) -> None:
    for i in range(3):
        await _create_note(client, title=f"Note {i}")

    response = await client.get("/notes", params={"limit": 2})

    assert len(response.json()) == 2


@pytest.mark.parametrize("limit", [0, 101])
async def test_list_rejects_out_of_range_limit(client: AsyncClient, limit: int) -> None:
    response = await client.get("/notes", params={"limit": limit})

    assert response.status_code == 422


# --- update ---


async def test_patch_changes_only_sent_fields(client: AsyncClient) -> None:
    created = await _create_note(client, title="Original", body="keep me", tags=["x"])

    response = await client.patch(f"/notes/{created['id']}", json={"title": "Renamed"})

    assert response.status_code == 200
    note = response.json()
    assert note["title"] == "Renamed"
    assert note["body"] == "keep me"
    assert note["tags"] == ["x"]


@pytest.mark.parametrize("field", ["title", "body", "tags"])
async def test_patch_rejects_explicit_null(client: AsyncClient, field: str) -> None:
    created = await _create_note(client)

    response = await client.patch(f"/notes/{created['id']}", json={field: None})

    assert response.status_code == 422


async def test_patch_missing_note_returns_404(client: AsyncClient) -> None:
    response = await client.patch(f"/notes/{MISSING_ID}", json={"title": "Whatever"})

    assert response.status_code == 404


# --- delete ---


async def test_delete_note(client: AsyncClient) -> None:
    created = await _create_note(client)

    response = await client.delete(f"/notes/{created['id']}")

    assert response.status_code == 204
    assert (await client.get(f"/notes/{created['id']}")).status_code == 404


async def test_delete_missing_note_returns_404(client: AsyncClient) -> None:
    response = await client.delete(f"/notes/{MISSING_ID}")

    assert response.status_code == 404


# --- helpers ---


async def _create_note(client: AsyncClient, **overrides: object) -> dict:
    payload = {"title": "Test note", **overrides}
    response = await client.post("/notes", json=payload)
    assert response.status_code == 201, response.text
    return response.json()
