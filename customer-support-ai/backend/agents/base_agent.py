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

    def _format_clean_fallback(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved context chunks into clean, elegant Markdown customer support response.
        Removes raw document titles, font encoding artifacts, and formats tabular data neatly.
        """
        import re

        if not chunks:
            return (
                f"I apologize, but I couldn't locate specific details for your query in our records. "
                f"Please allow our {self.name.capitalize()} support team to assist you further."
            )

        table_rows = []
        text_bullets = []

        for chunk in chunks[:4]:
            raw_text = chunk.get("text", "").strip()
            # Clean up font artifacts like (cid:127) and extra whitespace
            cleaned_text = re.sub(r'\(cid:\d+\)', '', raw_text)
            cleaned_text = re.sub(r'[ \t]+', ' ', cleaned_text).strip()

            if cleaned_text.startswith("Source Dataset:"):
                continue

            lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]
            for line in lines:
                if line.startswith("Source Dataset:"):
                    continue

                if "||" in line:
                    sub_segments = [seg.strip() for seg in line.split("||") if seg.strip()]
                    for seg in sub_segments:
                        parts = [p.strip() for p in seg.split("|") if p.strip()]
                        if len(parts) >= 2:
                            table_rows.append(parts)
                        elif seg:
                            text_bullets.append(seg)
                elif "|" in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 2:
                        table_rows.append(parts)
                    elif line:
                        text_bullets.append(line)
                else:
                    if line:
                        text_bullets.append(line)

        formatted_sections = []

        if table_rows:
            unique_rows = []
            seen_tuples = set()
            for r in table_rows:
                t = tuple(r)
                if t not in seen_tuples and not all(c.startswith("-") for c in r):
                    seen_tuples.add(t)
                    unique_rows.append(r)

            if unique_rows:
                num_cols = max(len(r) for r in unique_rows)
                header = list(unique_rows[0])
                data_rows = unique_rows[1:] if len(unique_rows) > 1 else unique_rows

                while len(header) < num_cols:
                    header.append(f"Detail {len(header)+1}")

                header_str = "| " + " | ".join(header) + " |"
                separator_str = "| " + " | ".join([":---"] * num_cols) + " |"

                body_lines = []
                for row in data_rows:
                    padded_row = list(row) + [""] * (num_cols - len(row))
                    body_lines.append("| " + " | ".join(padded_row) + " |")

                markdown_table = "\n".join([header_str, separator_str] + body_lines)
                formatted_sections.append(markdown_table)

        if text_bullets:
            unique_bullets = []
            seen_b = set()
            for b in text_bullets:
                if b not in seen_b:
                    seen_b.add(b)
                    clean_b = re.sub(r'^[•\-\*]\s*', '', b).strip()
                    if clean_b:
                        unique_bullets.append(f"• {clean_b}")

            if unique_bullets:
                formatted_sections.append("\n".join(unique_bullets[:5]))

        final_body = "\n\n".join(formatted_sections) if formatted_sections else "Here are the relevant details from our records."

        return (
            f"Here are the relevant details from our verified records:\n\n"
            f"{final_body}\n\n"
            f"Please let me know if you need any additional clarification!"
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
            response_text = self._format_clean_fallback(chunks)

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
            response_text = self._format_clean_fallback(chunks)

        return AgentResponse(
            text=response_text,
            agent_name=self.name,
            source_docs=sources,
            confidence=1.0 if chunks else 0.8,
            raw_chunks=chunks,
        )
