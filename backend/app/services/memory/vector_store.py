# backend/app/services/memory/vector_store.py
import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List, Dict, Any, Optional
import numpy as np
from app.config import get_settings
from app.services.sambanova_client import SambaNovaOrchestrator
from pathlib import Path
import asyncio


class CodebaseVectorStore:
    """
    ChromaDB wrapper optimized for code retrieval.
    Supports multi-tenant isolation per workspace/project.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.sambanova = SambaNovaOrchestrator()

        
        
        self.client = chromadb.PersistentClient(
            path=self.settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Collection per project/workspace
        self._collections = {}
    
    def get_collection(self, workspace_id: str):
        """Get or create collection for workspace."""
        if workspace_id not in self._collections:
            self._collections[workspace_id] = self.client.get_or_create_collection(
                name=f"codebase_{workspace_id}",
                metadata={"hnsw:space": "cosine"},
                embedding_function=None  # We provide embeddings manually
            )
        return self._collections[workspace_id]
    
    async def ingest_code_chunks(
        self,
        workspace_id: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Batch ingest code chunks with SambaNova embeddings.
        """
        collection = self.get_collection(workspace_id)
        
        # Generate embeddings in batches
        batch_size = 32
        all_embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [c["embedding_text"] for c in batch]
            
            # Parallel embedding generation
            embeddings = await asyncio.gather(*[
                self.sambanova.create_code_embedding(text, c["file_path"])
                for text, c in zip(texts, batch)
            ])
            all_embeddings.extend(embeddings)
        
        # Prepare for Chroma
        ids = [f"{c['file_path']}:{c['content_hash']}" for c in chunks]
        documents = [c["embedding_text"] for c in chunks]
        metadatas = [{
            "file_path": c["file_path"],
            "line_start": c["line_start"],
            "line_end": c["line_end"],
            "construct_type": c.get("construct_type", "unknown"),
            "name": c.get("name", ""),
            "language": c["language"]
        } for c in chunks]
        
        # Upsert in batches
        collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=all_embeddings,
            metadatas=metadatas
        )
        
        return {
            "ingested_count": len(chunks),
            "workspace_id": workspace_id,
            "unique_files": len(set(c["file_path"] for c in chunks))
        }
    
    async def search(
    self,
    workspace_id: str,
    query: str,
    filters: Optional[Dict[str, Any]] = None,
    top_k: int = 5
    ) -> List[Dict[str, Any]]:
        top_k = max(top_k, 1)
        """
        Semantic search over codebase with optional filters.
        """
        collection = self.get_collection(workspace_id)
        
        # Generate query embedding
        query_embedding = await self.sambanova.create_embedding(
            f"Given a code query, retrieve relevant code snippets: {query}"
        )
        
        # Build where clause for filters
        where_clause = {}
        if filters:
            if "language" in filters:
                where_clause["language"] = filters["language"]
            if "file_path" in filters:
                where_clause["file_path"] = {"$contains": filters["file_path"]}
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted = []
        for i in range(len(results["ids"][0])):
            formatted.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
                "score": 1 - results["distances"][0][i]  # Convert to similarity
            })
        
        return formatted
    
    async def hybrid_search(
        self,
        workspace_id: str,
        query: str,
        code_location: Optional[Dict[str, str]] = None,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Combine semantic search with location-based boosting.
        """
        # Get semantic results
        semantic_results = await self.search(workspace_id, query, top_k=top_k * 2)
        
        if not code_location:
            return semantic_results[:top_k]
        
        # Boost results from same/nearby files
        target_file = code_location.get("file_path", "")
        
        def score_result(result):
            base_score = result["score"]
            file_path = result["metadata"]["file_path"]
            
            # Exact file match
            if file_path == target_file:
                return base_score * 1.5
            
            # Same directory
            if Path(file_path).parent == Path(target_file).parent:
                return base_score * 1.2
            
            # Same extension
            if Path(file_path).suffix == Path(target_file).suffix:
                return base_score * 1.1
            
            return base_score
        
        # Re-rank and return top_k
        scored = [(score_result(r), r) for r in semantic_results]
        scored.sort(key=lambda x: x[0], reverse=True)
        
        return [r for _, r in scored[:top_k]]