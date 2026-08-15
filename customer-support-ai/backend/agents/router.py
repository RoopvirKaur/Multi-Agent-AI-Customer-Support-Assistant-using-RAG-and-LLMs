"""
router.py
Agent Router for Multi-Agent AI system.
Routes detected intents to responsible specialized agent instances and dispatches them in parallel.
"""

import asyncio
import logging
from typing import List, Dict, Optional, Any, Type

from backend.agents.base_agent import BaseAgent, AgentResponse
from backend.agents.billing import BillingAgent
from backend.agents.technical import TechnicalAgent
from backend.agents.product import ProductAgent
from backend.agents.complaint import ComplaintAgent
from backend.agents.faq import FAQAgent
from backend.utils.logger import get_logger

logger = get_logger("agent_router")

ROUTING_MAP: Dict[str, Type[BaseAgent]] = {
    "billing": BillingAgent,
    "refund": BillingAgent,
    "technical": TechnicalAgent,
    "technical_support": TechnicalAgent,
    "product": ProductAgent,
    "complaint": ComplaintAgent,
    "faq": FAQAgent,
    "general_faq": FAQAgent,
}


class AgentRouter:
    """
    Orchestrates mapping from classified intent labels to specialized agents,
    and manages concurrent execution across agents.
    """

    def __init__(self):
        # Pre-instantiate singletons for performance
        self.billing_agent = BillingAgent()
        self.technical_agent = TechnicalAgent()
        self.product_agent = ProductAgent()
        self.complaint_agent = ComplaintAgent()
        self.faq_agent = FAQAgent()

        self._instances: Dict[str, BaseAgent] = {
            "billing": self.billing_agent,
            "refund": self.billing_agent,
            "technical": self.technical_agent,
            "technical_support": self.technical_agent,
            "product": self.product_agent,
            "complaint": self.complaint_agent,
            "faq": self.faq_agent,
            "general_faq": self.faq_agent,
        }

    def route(self, intents: List[str]) -> List[BaseAgent]:
        """
        Map a list of intent labels to a deduplicated list of specialized agents.
        """
        selected_agents: List[BaseAgent] = []
        seen_names = set()

        for intent in intents:
            norm = str(intent).strip().lower()
            agent = self._instances.get(norm)
            if agent and agent.name not in seen_names:
                seen_names.add(agent.name)
                selected_agents.append(agent)

        # Fallback to FAQ agent if no match found
        if not selected_agents:
            selected_agents.append(self.faq_agent)

        return selected_agents

    async def dispatch_all(
        self,
        agents: List[BaseAgent],
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[AgentResponse]:
        """
        Concurrently execute all selected agents using asyncio.gather.
        Catches and isolates individual agent exceptions.
        """
        if not agents:
            agents = [self.faq_agent]

        tasks = [agent.run(query=query, history=history) for agent in agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_responses: List[AgentResponse] = []
        for i, res in enumerate(results):
            agent_name = agents[i].name
            if isinstance(res, Exception):
                logger.error(f"Agent '{agent_name}' raised an unhandled exception: {res}")
            elif isinstance(res, AgentResponse):
                successful_responses.append(res)
            else:
                logger.warning(f"Agent '{agent_name}' returned unexpected type: {type(res)}")

        # Fallback if every agent failed
        if not successful_responses:
            logger.error("All dispatched agents failed to produce a valid response.")
            successful_responses.append(
                AgentResponse(
                    text="Our support systems are currently experiencing delays. Please try again shortly or contact support@techmart.com.",
                    agent_name="faq",
                    source_docs=[],
                    confidence=0.5,
                )
            )

        return successful_responses

    def dispatch_all_sync(
        self,
        agents: List[BaseAgent],
        query: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> List[AgentResponse]:
        """
        Synchronously execute all selected agents.
        """
        if not agents:
            agents = [self.faq_agent]

        successful_responses: List[AgentResponse] = []
        for agent in agents:
            try:
                res = agent.run_sync(query=query, history=history)
                successful_responses.append(res)
            except Exception as e:
                logger.error(f"Agent '{agent.name}' sync failed: {e}")

        if not successful_responses:
            successful_responses.append(
                AgentResponse(
                    text="Our support systems are currently experiencing delays. Please try again shortly or contact support@techmart.com.",
                    agent_name="faq",
                    source_docs=[],
                    confidence=0.5,
                )
            )

        return successful_responses


# Global singleton
_agent_router: Optional[AgentRouter] = None


def get_agent_router() -> AgentRouter:
    """Dependency accessor function for global AgentRouter singleton."""
    global _agent_router
    if _agent_router is None:
        _agent_router = AgentRouter()
    return _agent_router
