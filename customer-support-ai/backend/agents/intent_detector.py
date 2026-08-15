"""
intent_detector.py
Intent Detection Agent for Multi-Agent AI system.
Performs zero-shot multi-label classification of incoming customer inquiries using Gemini LLM.
"""

import json
import re
import logging
from typing import List, Dict, Optional, Any

from backend.llm.gemini_client import GeminiClient, get_gemini_client
from backend.utils.logger import get_logger

logger = get_logger("intent_detector")

VALID_INTENTS = {"billing", "technical", "product", "complaint", "faq"}

SYNONYM_MAP = {
    "refund": "billing",
    "refunds": "billing",
    "payment": "billing",
    "pricing": "billing",
    "invoice": "billing",
    "subscription": "billing",
    "technical_support": "technical",
    "tech": "technical",
    "troubleshooting": "technical",
    "installation": "technical",
    "setup": "technical",
    "products": "product",
    "features": "product",
    "complaints": "complaint",
    "escalation": "complaint",
    "general_faq": "faq",
    "general": "faq",
    "shipping": "faq",
    "warranty": "faq",
}

INTENT_CLASSIFICATION_PROMPT = """
You are an expert intent classification system for TechMart Electronics customer support.
Classify the customer message into one or more of the following standard intent domains:

- "billing": questions about payment methods, duplicate charges, billing disputes, subscriptions, invoices, pricing plans, returns, and refund requests.
- "technical": device not turning on, power issues, product setup, device installation, login/password problems, app syncing, error codes, hardware bugs, and troubleshooting.
- "product": technical specifications, features, model comparisons (Standard vs Pro), compatibility, and product catalog availability.
- "complaint": customer dissatisfaction, delayed shipments, broken items, angry feedback, and escalation requests.
- "faq": general inquiries, store hours, contact info, shipping delivery times, and warranty overview.

CRITICAL INSTRUCTIONS:
1. Multi-intent / Compound messages: If the user describes multiple distinct issues (e.g. "I was charged twice and my device won't turn on", or "How much is Pro and how do I install it?"), you MUST identify and include ALL relevant intents.
2. Return ONLY a valid JSON array of strings, e.g. ["billing", "technical"] or ["billing"].
3. Do not include markdown formatting, backticks, or extra words.
""".strip()


class IntentDetector:
    """
    Classifies user messages into one or more specialized domain intents.
    """

    def __init__(self, llm_client: Optional[GeminiClient] = None):
        self.llm_client = llm_client or get_gemini_client()

    def _normalize_intents(self, raw_intents: List[str]) -> List[str]:
        """
        Normalize intent labels through synonym mapping and deduplicate.
        """
        normalized = []
        for raw in raw_intents:
            cleaned = str(raw).strip().lower().replace("-", "_").replace(" ", "_")
            # Map synonyms
            canonical = SYNONYM_MAP.get(cleaned, cleaned)
            if canonical in VALID_INTENTS and canonical not in normalized:
                normalized.append(canonical)

        # Fallback to default if no valid intent recognized
        if not normalized:
            normalized = ["faq"]
        return normalized

    def _parse_llm_output(self, response_text: str) -> List[str]:
        """
        Extract and parse JSON array from LLM response text.
        """
        if not response_text or not response_text.strip():
            return ["faq"]

        cleaned = response_text.strip()
        # Remove potential markdown fences
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned)

        # Look for JSON array pattern
        match = re.search(r"\[.*?\]", cleaned, re.DOTALL)
        if match:
            array_str = match.group(0)
            try:
                parsed = json.loads(array_str)
                if isinstance(parsed, list):
                    return self._normalize_intents(parsed)
            except Exception as e:
                logger.warning(f"Failed to parse JSON intent array '{array_str}': {e}")

        # Fallback regex extraction of known keywords
        extracted = []
        for intent in VALID_INTENTS | set(SYNONYM_MAP.keys()):
            if re.search(rf"\b{intent}\b", cleaned, re.IGNORECASE):
                extracted.append(intent)

        if extracted:
            return self._normalize_intents(extracted)

        return ["faq"]

    def detect(
        self,
        message: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Synchronously classify user inquiry into list of intent strings.
        """
        if not message or not message.strip():
            return ["faq"]

        try:
            raw_response = self.llm_client.generate(
                system_prompt=INTENT_CLASSIFICATION_PROMPT,
                user_message=f"Customer message: \"{message.strip()}\"",
                history=history,
                temperature=0.0,
                max_output_tokens=100,
            )
            return self._parse_llm_output(raw_response)
        except Exception as e:
            logger.error(f"Intent detection LLM call failed: {e}. Falling back to ['faq'].")
            return ["faq"]

    async def adetect(
        self,
        message: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """
        Asynchronously classify user inquiry into list of intent strings.
        """
        if not message or not message.strip():
            return ["faq"]

        try:
            raw_response = await self.llm_client.agenerate(
                system_prompt=INTENT_CLASSIFICATION_PROMPT,
                user_message=f"Customer message: \"{message.strip()}\"",
                history=history,
                temperature=0.0,
                max_output_tokens=100,
            )
            return self._parse_llm_output(raw_response)
        except Exception as e:
            logger.error(f"Async intent detection LLM call failed: {e}. Falling back to ['faq'].")
            return ["faq"]


# Global singleton
_intent_detector: Optional[IntentDetector] = None


def get_intent_detector() -> IntentDetector:
    """Dependency accessor function for global IntentDetector instance."""
    global _intent_detector
    if _intent_detector is None:
        _intent_detector = IntentDetector()
    return _intent_detector
