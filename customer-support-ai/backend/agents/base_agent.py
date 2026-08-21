"""
base_agent.py
Abstract base class and response contract for all specialized AI customer support agents.
Integrates scoped RAG retrieval and LLM response generation.
"""

import time
from abc import ABC
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from backend.rag.retriever import Retriever, get_retriever
from backend.llm.gemini_client import GeminiClient, get_gemini_client
from backend.utils.logger import get_logger

logger = get_logger("base_agent")



@dataclass
class AgentResponse:
    """
    Standardized response emitted by an individual specialized agent.
    """
    text: str
    agent_name: str
    source_docs: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 1.0
    raw_chunks: List[Dict[str, Any]] = field(default_factory=list)


class BaseAgent(ABC):
    """
    Abstract Base Agent encapsulating persona system prompt, domain scope,
    RAG retrieval, and response synthesis.
    """

    name: str = "base"
    system_prompt: str = ""
    agent_scope: str = "faq"

    def __init__(
        self,
        retriever: Optional[Retriever] = None,
        llm_client: Optional[GeminiClient] = None,
    ):
        self.retriever = retriever or get_retriever()
        self.llm_client = llm_client or get_gemini_client()

    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        min_similarity: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Fetch top-k relevant knowledge base chunks filtered by agent_scope.
        """
        try:
            return self.retriever.retrieve(
                query=query,
                agent_scope=self.agent_scope,
                top_k=top_k,
                min_similarity=min_similarity,
            )
        except Exception as e:
            logger.error(f"Error retrieving context for agent '{self.name}': {e}")
            return []

    def _extract_source_docs(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract and deduplicate source document references from retrieved chunks.
        """
        seen = set()
        sources = []
        for chunk in chunks:
            doc = chunk.get("document") or chunk.get("document_title") or "KnowledgeBase.pdf"
            page = chunk.get("page")
            key = (doc, page)
            if key not in seen:
                seen.add(key)
                sources.append({"document": doc, "page": page})
        return sources

    def generate_response(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Synchronously call the LLM with the agent's system prompt, retrieved context, and history.
        """
        return self.llm_client.generate(
            system_prompt=self.system_prompt,
            user_message=query,
            history=history,
            context=context,
            temperature=0.3,
        )

    async def generate_response_async(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Asynchronously call the LLM with the agent's system prompt, retrieved context, and history.
        """
        return await self.llm_client.agenerate(
            system_prompt=self.system_prompt,
            user_message=query,
            history=history,
            context=context,
            temperature=0.3,
        )

    async def run(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentResponse:
        """
        Asynchronously execute agent workflow: Scoped Retrieve -> Grounded Generate -> Return AgentResponse.
        """
        start_time = time.time()
        logger.info(f"Executing agent '{self.name}' for query: {query[:60]}...")
        # 1. Scoped Retrieval
        t_rag = time.time()
        chunks = self.retrieve_context(query)
        sources = self._extract_source_docs(chunks)
        rag_ms = (time.time() - t_rag) * 1000

        # 2. Async LLM Generation
        status = "success"
        try:
            response_text = await self.generate_response_async(
                query=query,
                history=history,
                context=chunks,
            )
        except Exception as e:
            status = f"error: {e}"
            logger.error(f"Agent '{self.name}' generation failed: {e}")
            if chunks:
                top_texts = [c.get("text", "") for c in chunks[:3] if c.get("text")]
                joined_context = "\n\n".join(top_texts)
                response_text = (
                    f"Here is the relevant information retrieved from our verified records:\n\n"
                    f"{joined_context}"
                )
            else:
                response_text = (
                    f"I encountered a temporary system limit while processing your request. "
                    f"Please allow our {self.name.capitalize()} team to assist you further or ask your question again in a moment."
                )

        total_ms = (time.time() - start_time) * 1000
        logger.log_agent_execution(
            agent_name=self.name,
            query=query,
            duration_ms=total_ms,
            chunks_count=len(chunks),
            sources=sources,
            status=status,
        )

        return AgentResponse(
            text=response_text,
            agent_name=self.name,
            source_docs=sources,
            confidence=1.0 if chunks else 0.8,
            raw_chunks=chunks,
        )

    def run_sync(
        self,
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> AgentResponse:
        """
        Synchronously execute agent workflow.
        """
        chunks = self.retrieve_context(query)
        sources = self._extract_source_docs(chunks)
        try:
            response_text = self.generate_response(
                query=query,
                history=history,
                context=chunks,
            )
        except Exception as e:
            logger.error(f"Agent '{self.name}' sync generation failed: {e}")
            if chunks:
                top_texts = [c.get("text", "") for c in chunks[:3] if c.get("text")]
                joined_context = "\n\n".join(top_texts)
                response_text = (
                    f"Here is the relevant information retrieved from our verified records:\n\n"
                    f"{joined_context}"
                )
            else:
                response_text = (
                    f"I encountered a temporary system limit while processing your request. "
                    f"Please allow our {self.name.capitalize()} team to assist you further or ask your question again in a moment."
                )

        return AgentResponse(
            text=response_text,
            agent_name=self.name,
            source_docs=sources,
            confidence=1.0 if chunks else 0.8,
            raw_chunks=chunks,
        )
