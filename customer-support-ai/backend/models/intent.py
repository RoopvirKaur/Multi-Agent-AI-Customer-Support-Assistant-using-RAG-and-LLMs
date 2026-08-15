"""
Pydantic schemas and Enums for Intent Detection.
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class IntentLabel(str, Enum):
    """Supported specialized agent domain intents."""
    BILLING = "billing"
    TECHNICAL = "technical"
    PRODUCT = "product"
    COMPLAINT = "complaint"
    FAQ = "faq"


class IntentResponse(BaseModel):
    """Structured response from the Intent Detection Agent."""
    intents: List[IntentLabel] = Field(..., description="One or more detected intents")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Classification confidence")
    reasoning: Optional[str] = Field(default=None, description="Brief explanation of intent classification")
