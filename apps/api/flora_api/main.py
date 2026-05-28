from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from flora_api.database import init_db
from flora_api.routes import audit, claims, jobs, patches, sources

app = FastAPI(title="Flora API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(sources.router)
app.include_router(jobs.router)
app.include_router(claims.router)
app.include_router(patches.router)
app.include_router(audit.router)
