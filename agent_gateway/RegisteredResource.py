from dataclasses import dataclass,field 
from typing import List, Dict, Any, Optional

@dataclass 
class RegisteredResource:
    # -- tool essentials information
    id: str 
    description: str 
    capabilities: List[str]
    endpoint: str 
    api_shcema: Dict[str,Any]
    manifest: Dict[str,Any]
    owner: str = ""

    # -- tool registration information
    registration_time: str = ""
    last_tested: Optional[str]

    # -- tool testing information
    test_results: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    usage_count: int = 0
    success_rate: float = 100.0
    avg_response_time: float = 0.0
    is_active: bool = True


