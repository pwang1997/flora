import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routes.document_versions import router as document_versions_router
from routes.source_documents import router as source_documents_router
from routes.sources import router as sources_router

import sys

if "pytest" not in sys.modules:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )


app = FastAPI(title="Flora Core", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sources_router)
app.include_router(source_documents_router)
app.include_router(document_versions_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "flora-core"}
