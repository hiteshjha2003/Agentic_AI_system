# backend/app/services/memory/conversation_store.py
import chromadb
import hashlib
from typing import List, Dict, Any, Optional
from app.config import get_settings
from app.services.sambanova_client import SambaNovaOrchestrator

class ConversationStore:
    """
    Stores and retrieves conversation history using ChromaDB.
    Supports semantic search over past interactions.
    """

    def __init__(self):
        self.settings = get_settings()
        self.sambanova = SambaNovaOrchestrator()
        self.client = chromadb.PersistentClient(
            path=self.settings.CHROMA_PERSIST_DIR + "/conversations"
        )
        self.collections = {}

    def get_collection(self, session_id: str):
        """Get or create conversation collection for a session."""
        if session_id not in self.collections:
            self.collections[session_id] = self.client.get_or_create_collection(
                name=f"conv_{session_id}",
                metadata={"hnsw:space": "cosine"}
            )
        return self.collections[session_id]

    async def store_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store a message with embedding."""
        collection = self.get_collection(session_id)

        embedding = await self.sambanova.create_embedding(content)

        msg_id = str(hashlib.md5(content.encode()).hexdigest())

        collection.add(
            ids=[msg_id],
            documents=[content],
            embeddings=[embedding],
            metadatas=[{"role": role, **(metadata or {})}]
        )

        return msg_id

    async def search_conversation(
        self,
        session_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search within a conversation session."""
        collection = self.get_collection(session_id)

        query_embedding = await self.sambanova.create_embedding(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        return [
            {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i]
            }
            for i in range(len(results["ids"][0]))
        ]

    def delete_session(self, session_id: str):
        """Delete entire conversation session."""
        self.client.delete_collection(f"conv_{session_id}")
        self.collections.pop(session_id, None)