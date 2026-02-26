# backend/app/services/analysis/context_engine.py
from typing import List, Dict, Any, Optional
import asyncio
import json
from app.services.memory.vector_store import CodebaseVectorStore
from app.services.sambanova_client import SambaNovaOrchestrator
from app.config import get_settings

class ContextEngine:
    """
    Manages context retrieval and augmentation for analysis.
    Combines vector search with recent conversations and user-provided hints.
    """

    def __init__(self):
        self.settings = get_settings()
        self.sambanova = SambaNovaOrchestrator()
        self.vector_store = CodebaseVectorStore()

    async def retrieve_context(
        self,
        workspace_id: str,
        query: str,
        analysis_type: str,
        code_location: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        max_contexts: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and rank relevant contexts from multiple sources.
        """
        # 1. Semantic search from vector store
        code_contexts = await self.vector_store.hybrid_search(
            workspace_id=workspace_id,
            query=query,
            code_location=code_location,
            top_k=max_contexts
        )

        # 2. Retrieve recent conversation snippets if available
        conversation_contexts = []
        if conversation_history:
            conversation_contexts = await self._extract_relevant_conversations(
                query, conversation_history
            )

        # 3. Combine and re-rank
        all_contexts = code_contexts + conversation_contexts

        # Re-rank with SambaNova for relevance
        reranked = await self._rerank_contexts(query, all_contexts, analysis_type)

        return reranked[:max_contexts]

    async def _extract_relevant_conversations(
        self,
        query: str,
        history: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Embed and search within recent conversation history.
        """
        # Simple embedding-based search
        history_embeddings = await asyncio.gather(*[
            self.sambanova.create_embedding(msg["content"])
            for msg in history
        ])

        query_embedding = await self.sambanova.create_embedding(query)

        # Compute cosine similarities
        from sklearn.metrics.pairwise import cosine_similarity
        similarities = cosine_similarity([query_embedding], history_embeddings)[0]

        # Select top 3
        top_indices = similarities.argsort()[-3:][::-1]
        return [
            {
                "id": f"conv_{i}",
                "content": history[i]["content"],
                "metadata": {"type": "conversation", "role": history[i]["role"]},
                "score": similarities[i]
            }
            for i in top_indices if similarities[i] > 0.7
        ]

    async def _rerank_contexts(
        self,
        query: str,
        contexts: List[Dict[str, Any]],
        analysis_type: str
    ) -> List[Dict[str, Any]]:
        """
        Use SambaNova to re-rank contexts for better precision.
        """
        if len(contexts) <= 5:
            return contexts  # No need for small sets

        # Format for model
        system_prompt = f"""You are a context relevance ranker for {analysis_type} tasks.
Rank the following contexts by relevance to the query: {query}
Output only a JSON array of indices in descending relevance order."""

        user_content = "\n".join([
            f"Context {i}: {ctx['content'][:500]}" for i, ctx in enumerate(contexts)
        ])

        response = await self.sambanova.client.chat.completions.create(
            model=self.sambanova.models["chat"],
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            max_tokens=512,
            temperature=0.0
        )

        try:
            ranked_indices = json.loads(response.choices[0].message.content)
            return [contexts[i] for i in ranked_indices if i < len(contexts)]
        except Exception:
            # Fallback to original order
            return sorted(contexts, key=lambda x: x.get("score", 0), reverse=True)