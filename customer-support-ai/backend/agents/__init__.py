"""
Agents package initialization.
Exports all specialized customer support agents, base classes, intent detector, router, and aggregator.
"""

from backend.agents.base_agent import BaseAgent, AgentResponse
from backend.agents.billing import BillingAgent
from backend.agents.technical import TechnicalAgent
from backend.agents.product import ProductAgent
from backend.agents.complaint import ComplaintAgent
from backend.agents.faq import FAQAgent
from backend.agents.intent_detector import IntentDetector, get_intent_detector
from backend.agents.router import AgentRouter, get_agent_router
from backend.agents.aggregator import ResponseAggregator, AggregatedResult, get_response_aggregator

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "BillingAgent",
    "TechnicalAgent",
    "ProductAgent",
    "ComplaintAgent",
    "FAQAgent",
    "IntentDetector",
    "get_intent_detector",
    "AgentRouter",
    "get_agent_router",
    "ResponseAggregator",
    "AggregatedResult",
    "get_response_aggregator",
]
