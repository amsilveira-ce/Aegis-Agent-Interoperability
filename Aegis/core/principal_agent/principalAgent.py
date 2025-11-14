from principalAgent_schemas import OperationalMode, Task, Resource
from typing import List, Dict, Any, Optional
import uuid
import logging


logger = logging.getLogger(__name__)

class PrincipalAgent:
    """
    Principal Agent acts as the central orchestrator in the DAWN framework.
    It plans tasks, requests resources from Gateway Agents, and orchestrates execution.
    """

    def __init__(self, name: str = "principal_agent", mode: OperationalMode = OperationalMode):
        self.name = name
        self.id = str(uuid.uuid4())
        self.mode = mode

        # Connected Gateway Agents
        self.gateway_agents = []

        # Local resource pool (cache)
        self.local_resources = {}

        # Task queue and execution history
        # might change based on a2a 
        self.task_queue = []
        self.execution_history = []


        # Context management
        self.context = {
            "conversation_history": [],
            "user_preferences": {},
            "task_history": [],
            "memory_bank": {}
        }

        # Reasoning strategies - basic 3 ones inspired on the paper 
        self.reasoning_strategies = {
            "react": self._reasoning_react,
            "rewoo": self._reasoning_rewoo,
            "tot": self._reasoning_tree_of_thoughts
        }

        self.current_strategy = "react"
        
        logger.info(f"Principal Agent '{self.name}' initialized in {mode.value} mode")


    def connect_gateway(self, gateway_agent):
        """Connect to a Gateway Agent"""
        self.gateway_agents.append(gateway_agent)
        logger.info(f"Connected to Gateway Agent: {gateway_agent.name}")
    
    async def plan_task(self, user_request: str) -> List[Task]:
        """
        Create a plan to execute the user's request.
        Decomposes the request into manageable subtasks.
        """
        logger.info(f"Planning task: {user_request}")

        tasks = []

        # Make simple rule based for mvp testing 
        if "calculate" in user_request.lower():
            tasks.append(Task(
                id=str(uuid.uuid4()),
                description="Perform arithmetic calculation",
                requirements=["arithmetic", "math"],
                context={"input": user_request}
            ))

        if "search" in user_request.lower():
            tasks.append(Task(
                id=str(uuid.uuid4()),
                description="Search for information",
                requirements=["search", "information_retrieval"],
                context={"query": user_request}
            ))

        if "analyze" in user_request.lower():
            tasks.append(Task(
                id=str(uuid.uuid4()),
                description="Analyze data",
                requirements=["data_analysis", "statistics"],
                context={"data": user_request}
            ))

         # Default task if no specific pattern matched
        if not tasks:
            tasks.append(Task(
                id=str(uuid.uuid4()),
                description=user_request,
                requirements=["general"],
                context={"original_request": user_request}
            ))
        
        self.task_queue.extend(tasks)
        return tasks

    async def request_resources(self, task: Task) -> List[Resource]:
        pass

    def _filter_resources(self, resources: List[Resource], requirements: List[str]) -> List[Resource]:
        pass 

    async def execute_task(self, user_request: str) -> Dict[str, Any]:
        pass 

    def _filter_resources(self, resources: List[Resource], requirements: List[str]) -> List[Resource]:
        pass

    async def execute_task(self, user_request: str) -> Dict[str, Any]:
        pass 
    
    # Before looking for resources we need to check the local resources 
    def _find_local_resource(self, requirements: List[str]) -> Optional[Resource]:
        pass 

    async def _execute_with_resource(self, task: Task, resource: Resource) -> Dict[str, Any]:
        pass 

    # ==== Reasoning Strategies ==== 
    # we need to force pre-done structured to help the llms in reflection 
    async def _reasoning_react(self, task: Task, observation: Any):
        pass

    async def _reasoning_rewoo(self, task: Task):
        pass 

    async def _reasoning_tree_of_thoughts(self, task: Task):
        pass

    def set_operation_mode(self, mode: OperationalMode):
        pass 
    
    # might change because of a2a usage 
    def get_execution_history(self) -> List[Dict]:
        pass 

    def get_context(self) -> Dict:
        pass