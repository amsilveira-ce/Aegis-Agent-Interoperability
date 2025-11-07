from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class OperationalMode(Enum):
    NO_LLM = "no_llm"          # Deterministic workflow
    ASSISTED = "assisted"      # Human-in-the-loop (Formerly Copilot)
    AGENT = "agent"            # Fully autonomous
    HYBRID = "hybrid"          # Combined modes


@dataclass 
class Task:
    # this can be done using the protocol A2A - future implementation 
    id: str
    description: str
    requirements: List[str]
    context: Dict[str, Any]
    status: str = "pending" # pending, on-going, "failed"
    result: Optional[Any] = None
    # this makes sense? maybe
    assigned_resource: Optional[str] = None


@dataclass
class Resource:
    id: str
    name: str
    capabilities: List[str]
    endpoint: str
    manifest: Dict[str, Any]
    gateway_id: str
    performance_metrics: Dict[str, float] = None
