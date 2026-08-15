"""
aggregator.py
Response Aggregator for Multi-Agent AI system.
Synthesizes individual agent outputs into a unified, coherent customer response.
Deduplicates sources and formats final message payload.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any

from backend.agents.base_agent import AgentResponse
from backend.llm.gemini_client import GeminiClient, get_gemini_client
from backend.utils.logger import get_logger

logger = get_logger("response_aggregator")

AGGREGATION_SYSTEM_PROMPT = """
You are the Lead Customer Support Orchestrator for TechMart Electronics.
You have received contributions from multiple specialized departments responding to a compound customer inquiry.
Your goal is to synthesize these individual department replies into a single, unified, coherent, and friendly response.

Guidelines:
1. Unified Voice: Present the answer seamlessly as one helpful TechMart customer support team.
2. Remove Duplications: Eliminate repetitive greetings (e.g. multiple "Hello"s or "Thank you for contacting TechMart") and duplicate farewells.
3. Preserve All Key Information: Retain all step-by-step instructions, policies, prices, numbers, and technical procedures provided by each department.
4. Clear Formatting: Use clear headings, bullet points, or numbered lists where appropriate so the customer can easily follow both parts of their answer.
5. Professional Tone: Maintain an empathetic, professional, and solutions-oriented tone.
""".strip()


@dataclass
class AggregatedResult:
    """Final unified result of the multi-agent orchestration."""
    text: str
    agents_invoked: List[str] = field(default_factory=list)
    sources: List[Dict[str, Any]] = field(default_factory=list)


class ResponseAggregator:
    """
    Combines responses from one or more specialized agents into a seamless customer-facing reply.
    """

    def __init__(self, llm_client: Optional[GeminiClient] = None):
        self.llm_client = llm_client or get_gemini_client()

    def _combine_sources(self, responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """
        Merge and deduplicate source document citations across all agents.
        """
        seen = set()
        combined = []
        for res in responses:
            for src in res.source_docs:
                doc = src.get("document") or "TechMart Knowledge Base"
                page = src.get("page")
                key = (doc, page)
                if key not in seen:
                    seen.add(key)
                    combined.append({"document": doc, "page": page})
        return combined

    def aggregate(
        self,
        responses: List[AgentResponse],
        query: str,
    ) -> AggregatedResult:
        """
        Synchronously aggregate agent responses.
        """
        # Filter out empty responses
        valid_responses = [r for r in responses if r.text and r.text.strip()]

        if not valid_responses:
            return AggregatedResult(
                text=(
                    "Thank you for contacting TechMart Electronics support. "
                    "We are currently experiencing high volume and could not process your inquiry immediately. "
                    "Please try again shortly or contact us at support@techmart.com."
                ),
                agents_invoked=[],
                sources=[],
            )

        # Single agent response: return as-is
        if len(valid_responses) == 1:
            res = valid_responses[0]
            return AggregatedResult(
                text=res.text.strip(),
                agents_invoked=[res.agent_name],
                sources=self._combine_sources(valid_responses),
            )

        # Multi-agent synthesis: call LLM to merge seamlessly
        agents_invoked = [r.agent_name for r in valid_responses]
        combined_sources = self._combine_sources(valid_responses)

        # Build synthesis prompt
        dept_replies = []
        for r in valid_responses:
            dept_replies.append(f"--- Department [{r.agent_name.upper()} SUPPORT] Response ---\n{r.text.strip()}")

        user_message_body = (
            f"Customer Inquiry: \"{query}\"\n\n"
            + "\n\n".join(dept_replies)
            + "\n\nPlease synthesize the above departmental responses into a unified, clear customer reply:"
        )

        try:
            synthesized_text = self.llm_client.generate(
                system_prompt=AGGREGATION_SYSTEM_PROMPT,
                user_message=user_message_body,
                temperature=0.3,
                max_output_tokens=1500,
            )
            return AggregatedResult(
                text=synthesized_text.strip(),
                agents_invoked=agents_invoked,
                sources=combined_sources,
            )
        except Exception as e:
            logger.error(f"Multi-agent synthesis failed: {e}. Joining responses sequentially.")
            joined_text = "\n\n".join([r.text.strip() for r in valid_responses])
            return AggregatedResult(
                text=joined_text,
                agents_invoked=agents_invoked,
                sources=combined_sources,
            )

    async def aaggregate(
        self,
        responses: List[AgentResponse],
        query: str,
    ) -> AggregatedResult:
        """
        Asynchronously aggregate agent responses.
        """
        valid_responses = [r for r in responses if r.text and r.text.strip()]

        if not valid_responses:
            return AggregatedResult(
                text=(
                    "Thank you for contacting TechMart Electronics support. "
                    "We are currently experiencing high volume and could not process your inquiry immediately. "
                    "Please try again shortly or contact us at support@techmart.com."
                ),
                agents_invoked=[],
                sources=[],
            )

        if len(valid_responses) == 1:
            res = valid_responses[0]
            return AggregatedResult(
                text=res.text.strip(),
                agents_invoked=[res.agent_name],
                sources=self._combine_sources(valid_responses),
            )

        agents_invoked = [r.agent_name for r in valid_responses]
        combined_sources = self._combine_sources(valid_responses)

        dept_replies = []
        for r in valid_responses:
            dept_replies.append(f"--- Department [{r.agent_name.upper()} SUPPORT] Response ---\n{r.text.strip()}")

        user_message_body = (
            f"Customer Inquiry: \"{query}\"\n\n"
            + "\n\n".join(dept_replies)
            + "\n\nPlease synthesize the above departmental responses into a unified, clear customer reply:"
        )

        try:
            synthesized_text = await self.llm_client.agenerate(
                system_prompt=AGGREGATION_SYSTEM_PROMPT,
                user_message=user_message_body,
                temperature=0.3,
                max_output_tokens=1500,
            )
            return AggregatedResult(
                text=synthesized_text.strip(),
                agents_invoked=agents_invoked,
                sources=combined_sources,
            )
        except Exception as e:
            logger.error(f"Async multi-agent synthesis failed: {e}. Joining responses sequentially.")
            joined_text = "\n\n".join([r.text.strip() for r in valid_responses])
            return AggregatedResult(
                text=joined_text,
                agents_invoked=agents_invoked,
                sources=combined_sources,
            )


# Global singleton
_response_aggregator: Optional[ResponseAggregator] = None


def get_response_aggregator() -> ResponseAggregator:
    """Dependency accessor function for global ResponseAggregator instance."""
    global _response_aggregator
    if _response_aggregator is None:
        _response_aggregator = ResponseAggregator()
    return _response_aggregator
