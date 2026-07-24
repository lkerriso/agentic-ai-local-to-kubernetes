"""Ingest this repository's documentation into the OGX vector store.

Creates (or reuses) a vector store named "knowledge_base" on the OGX
server, chunks the markdown files in docs/ plus README.md, embeds them
with the all-minilm model, and inserts the chunks so the agent's
search_documents tool has something to search.

Usage:
    uv run python examples/ingest_docs.py
"""

import sys
from os import getenv
from pathlib import Path

import httpx

OGX_BASE_URL = getenv("OGX_BASE_URL", "http://localhost:8321")
EMBEDDING_MODEL = "ollama/all-minilm:latest"
EMBEDDING_DIMENSION = 384
VECTOR_STORE_NAME = "knowledge_base"
CHUNK_SIZE = 1000

REPO_ROOT = Path(__file__).parent.parent


def chunk_text(text: str, size: int = CHUNK_SIZE) -> list[str]:
    """Split text into chunks of roughly `size` chars on paragraph breaks."""
    chunks = []
    current = ""
    for para in text.split("\n\n"):
        if len(current) + len(para) > size and current:
            chunks.append(current.strip())
            current = ""
        current += para + "\n\n"
    if current.strip():
        chunks.append(current.strip())
    return chunks


def get_or_create_store(client: httpx.Client) -> str:
    stores = client.get("/v1/vector_stores").json()
    for store in stores.get("data", []):
        if store.get("name") == VECTOR_STORE_NAME:
            print(f"Using existing vector store {store['id']}")
            return store["id"]
    resp = client.post(
        "/v1/vector_stores",
        json={
            "name": VECTOR_STORE_NAME,
            "embedding_model": EMBEDDING_MODEL,
            "embedding_dimension": EMBEDDING_DIMENSION,
        },
    )
    resp.raise_for_status()
    store_id = resp.json()["id"]
    print(f"Created vector store {store_id}")
    return store_id


def main() -> int:
    files = sorted((REPO_ROOT / "docs").glob("*.md")) + [REPO_ROOT / "README.md"]
    if not files:
        print("No markdown files found to ingest")
        return 1

    with httpx.Client(base_url=OGX_BASE_URL, timeout=120) as client:
        try:
            client.get("/v1/health").raise_for_status()
        except Exception as e:
            print(f"OGX server not reachable at {OGX_BASE_URL}: {e}")
            print("Start it with: cd local && make ogx-server")
            return 1

        store_id = get_or_create_store(client)

        total = 0
        for path in files:
            doc_id = path.relative_to(REPO_ROOT).as_posix()
            texts = chunk_text(path.read_text())

            embeddings = client.post(
                "/v1/embeddings",
                json={"model": EMBEDDING_MODEL, "input": texts},
            )
            embeddings.raise_for_status()
            vectors = [d["embedding"] for d in embeddings.json()["data"]]

            chunks = [
                {
                    "chunk_id": f"{doc_id}-{i}",
                    "content": text,
                    "metadata": {"document_id": doc_id},
                    "chunk_metadata": {"document_id": doc_id, "source": doc_id},
                    "embedding": vector,
                    "embedding_model": EMBEDDING_MODEL,
                    "embedding_dimension": EMBEDDING_DIMENSION,
                }
                for i, (text, vector) in enumerate(zip(texts, vectors))
            ]
            resp = client.post(
                "/v1/vector-io/insert",
                json={"vector_store_id": store_id, "chunks": chunks},
            )
            resp.raise_for_status()
            print(f"Ingested {doc_id}: {len(chunks)} chunks")
            total += len(chunks)

    print(f"Done: {total} chunks from {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
