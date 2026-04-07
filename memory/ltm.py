"""
Long-Term Memory (LTM) — off-stage vector archive in GWT.

Backed by ChromaDB for persistence. Embeddings are obtained via an
OpenAI-compatible embeddings endpoint, keeping the stack fully unified.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

import chromadb
from openai import OpenAI


class LongTermMemory:
    """
    Persistent vector store powering RAG retrieval (§3.5).

    All text is embedded via the configured API; ChromaDB handles similarity
    search and persistence across sessions.
    """

    def __init__(
        self,
        api_base_url: str,
        api_key: str,
        embedding_model: str,
        persist_dir: str = "./chroma_db",
        collection_name: str = "gwa_ltm",
    ) -> None:
        self._client = OpenAI(base_url=api_base_url, api_key=api_key)
        self._embedding_model = embedding_model

        self._chroma = chromadb.PersistentClient(path=persist_dir)
        self._collection = self._chroma.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    # ── Embedding ─────────────────────────────────────────────────────────────

    def embed(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts using the configured OpenAI-compatible API."""
        response = self._client.embeddings.create(
            model=self._embedding_model,
            input=texts,
        )
        return [item.embedding for item in response.data]

    # ── Store & Retrieve ──────────────────────────────────────────────────────

    def store(self, text: str, metadata: Optional[dict] = None) -> str:
        """Embed and persist a text chunk. Returns the assigned document ID."""
        doc_id = str(uuid.uuid4())
        embedding = self.embed([text])[0]
        self._collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}],
        )
        return doc_id

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        """Retrieve the top-k most semantically similar chunks for a query."""
        if self._collection.count() == 0:
            return []
        embedding = self.embed([query])[0]
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=min(top_k, self._collection.count()),
            include=["documents"],
        )
        docs: List[str] = results.get("documents", [[]])[0]
        return docs

    def retrieve_multi(self, queries: List[str], top_k: int = 3) -> str:
        """Retrieve for multiple queries and return a de-duplicated context string."""
        seen: set = set()
        chunks: List[str] = []
        for q in queries:
            for doc in self.retrieve(q, top_k=top_k):
                if doc not in seen:
                    seen.add(doc)
                    chunks.append(doc)
        return "\n---\n".join(chunks) if chunks else ""

    def count(self) -> int:
        return self._collection.count()
