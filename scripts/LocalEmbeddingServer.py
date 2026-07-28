from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    from fastembed import TextEmbedding
except Exception as exc:  # pragma: no cover - surfaced at startup
    raise RuntimeError("fastembed is required for the local embedding server") from exc


MODEL_NAME = os.environ.get("DEEPTUTOR_LOCAL_EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
INSTALL_DIR = Path(os.environ.get("DEEPTUTOR_HOME", r"D:\Backup\Documents\EC"))
CACHE_DIR = Path(
    os.environ.get(
        "DEEPTUTOR_FASTEMBED_CACHE",
        str(INSTALL_DIR / "data" / "user" / "models" / "fastembed"),
    )
)

app = FastAPI(title="DeepTutor Local Embedding Server", version="1.0.0")
_model: TextEmbedding | None = None


class EmbeddingRequest(BaseModel):
    model: str | None = None
    input: str | list[str] = Field(..., alias="input")
    encoding_format: str | None = None
    dimensions: int | None = None


def get_model() -> TextEmbedding:
    global _model
    if _model is None:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR))
    return _model


def normalize_inputs(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [value]
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise HTTPException(status_code=400, detail="input must be a string or list of strings")
    if not value:
        raise HTTPException(status_code=400, detail="input must not be empty")
    return value


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "model": MODEL_NAME}


@app.get("/v1/models")
def models() -> dict[str, Any]:
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "created": 0,
                "owned_by": "local-fastembed",
            }
        ],
    }


@app.post("/v1/embeddings")
def embeddings(request: EmbeddingRequest) -> dict[str, Any]:
    if request.dimensions not in (None, 384):
        raise HTTPException(
            status_code=400,
            detail="This local model only supports its native 384 dimensions",
        )

    texts = normalize_inputs(request.input)
    started = time.perf_counter()
    vectors = [vector.tolist() for vector in get_model().embed(texts)]
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    return {
        "object": "list",
        "data": [
            {"object": "embedding", "index": index, "embedding": vector}
            for index, vector in enumerate(vectors)
        ],
        "model": MODEL_NAME,
        "usage": {
            "prompt_tokens": 0,
            "total_tokens": 0,
            "items": len(texts),
            "elapsed_ms": elapsed_ms,
        },
    }


if __name__ == "__main__":
    host = os.environ.get("DEEPTUTOR_EMBEDDING_HOST", "127.0.0.1")
    port = int(os.environ.get("DEEPTUTOR_EMBEDDING_PORT", "8791"))
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=False,
    )
