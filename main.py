from fastapi import FastAPI

from app.routers import notes

app = FastAPI(title="doc-assistant")
app.include_router(notes.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
