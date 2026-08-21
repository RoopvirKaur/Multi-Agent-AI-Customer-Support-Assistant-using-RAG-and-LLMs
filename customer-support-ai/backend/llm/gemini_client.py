"""
gemini_client.py
Robust Google Gemini LLM client wrapper for Multi-Agent AI system.
Handles system prompt injection, RAG context formatting, conversation history,
retries with backoff, model fallback, and async execution.
"""

import os
import time
import asyncio
import logging
from typing import List, Dict, Optional, Any
import google.generativeai as genai
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

logger = logging.getLogger("gemini_client")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

DEFAULT_MODEL_CANDIDATES = [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]


class GeminiClient:
    """
    Client for interacting with Google Gemini models.
    Supports single-turn and multi-turn generation with RAG context grounding.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
        if not self.api_key:
            logger.warning("GEMINI_API_KEY is not set in environment or constructor.")
        else:
            genai.configure(api_key=self.api_key)

        preferred_model = model_name or os.getenv("GEMINI_MODEL")
        if preferred_model:
            self.model_candidates = [preferred_model] + [
                m for m in DEFAULT_MODEL_CANDIDATES if m != preferred_model
            ]
        else:
            self.model_candidates = list(DEFAULT_MODEL_CANDIDATES)

        self._active_model_name: Optional[str] = None

    def format_prompt(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Format system prompt, RAG context chunks, conversation history, and user message into a single coherent prompt.
        """
        sections = []

        # 1. System Prompt & Persona
        if system_prompt and system_prompt.strip():
            sections.append(f"### SYSTEM INSTRUCTION & ROLE:\n{system_prompt.strip()}")

        # 2. RAG Knowledge Base Context
        if context and len(context) > 0:
            context_blocks = []
            for i, chunk in enumerate(context, 1):
                doc_name = chunk.get("document") or chunk.get("document_title") or "Company Policy"
                page = chunk.get("page")
                page_str = f" (Page {page})" if page is not None else ""
                text = chunk.get("text", "").strip()
                context_blocks.append(f"[Source {i}: {doc_name}{page_str}]\n{text}")

            sections.append(
                "### VERIFIED KNOWLEDGE BASE CONTEXT (Ground your answer strictly in these facts):\n"
                + "\n\n".join(context_blocks)
            )

        # 3. Conversation History
        if history and len(history) > 0:
            history_blocks = []
            for item in history:
                role = item.get("role", "user").capitalize()
                content = item.get("content", "").strip()
                if content:
                    history_blocks.append(f"{role}: {content}")

            if history_blocks:
                sections.append(
                    "### RECENT CONVERSATION HISTORY:\n" + "\n".join(history_blocks)
                )

        # 4. Current Customer Inquiry
        sections.append(
            f"### CURRENT CUSTOMER MESSAGE:\nCustomer: {user_message.strip()}\n\n"
            "### ASSISTANT RESPONSE:"
        )

        return "\n\n".join(sections)

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = 1024,
        max_retries: int = 3,
    ) -> str:
        """
        Synchronously call Gemini with retry and model fallback.
        """
        if not self.api_key:
            self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
            if self.api_key:
                genai.configure(api_key=self.api_key)
            else:
                raise RuntimeError(
                    "GEMINI_API_KEY is not set. Please set GEMINI_API_KEY in your Render environment variables."
                )

        full_prompt = self.format_prompt(
            system_prompt=system_prompt,
            user_message=user_message,
            history=history,
            context=context,
        )

        generation_config = {
            "temperature": temperature,
        }
        if max_output_tokens:
            generation_config["max_output_tokens"] = max_output_tokens

        last_error = None

        # Build candidate list starting from active model if present
        candidates = list(self.model_candidates)
        if self._active_model_name and self._active_model_name in candidates:
            candidates.remove(self._active_model_name)
            candidates.insert(0, self._active_model_name)

        # Iterate through model candidates
        for model_name in candidates:
            model = genai.GenerativeModel(model_name)
            for attempt in range(1, max_retries + 1):
                try:
                    response = model.generate_content(
                        full_prompt,
                        generation_config=generation_config,
                    )
                    if response and response.text:
                        self._active_model_name = model_name
                        return response.text.strip()
                    else:
                        raise ValueError("Empty response text from Gemini API")
                except Exception as e:
                    last_error = e
                    err_str = str(e).lower()

                    if "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str:
                        logger.warning(f"Model '{model_name}' hit rate limit (attempt {attempt}/{max_retries}). Backing off...")
                        time.sleep(2.5 * attempt)
                    elif "404" in err_str:
                        logger.warning(f"Model '{model_name}' returned 404. Switching candidate...")
                        break
                    else:
                        if attempt < max_retries:
                            time.sleep(1.0 * attempt)
                        else:
                            break

        logger.error(f"All Gemini generation attempts failed. Last error: {last_error}")
        raise RuntimeError(f"Gemini API generation failed: {last_error}")

    async def agenerate(
        self,
        system_prompt: str,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.3,
        max_output_tokens: Optional[int] = 1024,
        max_retries: int = 2,
    ) -> str:
        """
        Asynchronously call Gemini using asyncio.to_thread for non-blocking execution in FastAPI.
        """
        return await asyncio.to_thread(
            self.generate,
            system_prompt=system_prompt,
            user_message=user_message,
            history=history,
            context=context,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            max_retries=max_retries,
        )


# Global singleton instance
_gemini_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Dependency accessor function for global GeminiClient singleton."""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
