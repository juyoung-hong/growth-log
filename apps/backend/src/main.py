from fastapi import FastAPI

from adapters.inbound.api.v1.persons import router as persons_router

app = FastAPI(title="Growth Log API")

app.include_router(persons_router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
