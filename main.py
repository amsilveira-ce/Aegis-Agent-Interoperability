"""
Principal Agent Implementation
Central orchestrator for the DAWN framework with MCP and A2A integration
"""

import asyncio
import json
import logging
from typing import List, Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class OperationMode(Enum):
    NO_LLM = "no_llm"          # Deterministic workflow
    COPILOT = "copilot"        # Human-in-the-loop
    AGENT = "agent"            # Fully autonomous
    HYBRID = "hybrid"          # Combined modes

@dataclass
class Task:
    id: str
    description: str
    requirements: List[str]
    context: Dict[str, Any]
    status: str = "pending"
    result: Optional[Any] = None
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

class PrincipalAgent:
    """
    Principal Agent acts as the central orchestrator in the DAWN framework.
    It plans tasks, requests resources from Gateway Agents, and orchestrates execution.
    """
    
    def __init__(self, 
                 name: str = "principal-agent",
                 mode: OperationMode = OperationMode.AGENT,
                 mcp_client=None,
                 a2a_protocol=None):
        self.name = name
        self.id = str(uuid.uuid4())
        self.mode = mode
        self.mcp_client = mcp_client
        self.a2a_protocol = a2a_protocol
        
        # Connected Gateway Agents
        self.gateway_agents = []
        
        # Local resource pool (cache)
        self.local_resources = {}
        
        # Task queue and execution history
        self.task_queue = []
        self.execution_history = []
        
        # Context management
        self.context = {
            "conversation_history": [],
            "user_preferences": {},
            "task_history": [],
            "memory_bank": {}
        }
        
        # Reasoning strategies
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
        
        # In production, this would use an LLM for planning
        # For MVP, using a simple rule-based decomposition
        tasks = []
        
        # Analyze request and create subtasks
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
        """
        Request suitable resources from connected Gateway Agents.
        Uses MCP for standardized resource discovery.
        """
        logger.info(f"Requesting resources for task: {task.description}")
        
        all_resources = []
        
        # Query each connected Gateway Agent
        for gateway in self.gateway_agents:
            try:
                # Use MCP protocol for resource discovery
                if self.mcp_client:
                    resources = await self.mcp_client.list_tools()
                else:
                    # Fallback to direct gateway query
                    resources = await gateway.search_resources(task.requirements)
                
                # Convert to Resource objects
                for res in resources:
                    resource = Resource(
                        id=res.get("id", str(uuid.uuid4())),
                        name=res["name"],
                        capabilities=res.get("capabilities", []),
                        endpoint=res.get("endpoint", ""),
                        manifest=res,
                        gateway_id=gateway.id
                    )
                    all_resources.append(resource)
                    
            except Exception as e:
                logger.error(f"Error querying gateway {gateway.name}: {e}")
        
        # Rank and filter resources based on requirements
        suitable_resources = self._filter_resources(all_resources, task.requirements)
        
        # Cache resources in local pool
        for resource in suitable_resources:
            self.local_resources[resource.id] = resource
        
        return suitable_resources
    
    def _filter_resources(self, resources: List[Resource], requirements: List[str]) -> List[Resource]:
        """Filter and rank resources based on task requirements"""
        suitable = []
        
        for resource in resources:
            # Check if resource capabilities match requirements
            if any(req in resource.capabilities for req in requirements):
                suitable.append(resource)
        
        # Sort by capability match count
        suitable.sort(key=lambda r: sum(1 for req in requirements if req in r.capabilities), reverse=True)
        
        return suitable
    
    async def execute_task(self, user_request: str) -> Dict[str, Any]:
        """
        Main execution method - plans and executes tasks based on user request.
        Implements the DAWN workflow with MCP and A2A integration.
        """
        logger.info(f"Executing request: {user_request}")
        
        # Add to context
        self.context["conversation_history"].append({
            "timestamp": datetime.now().isoformat(),
            "request": user_request
        })
        
        # Plan tasks
        tasks = await self.plan_task(user_request)
        
        results = []
        
        # Execute each task
        for task in tasks:
            try:
                # Check local resources first
                local_resource = self._find_local_resource(task.requirements)
                
                if local_resource:
                    # Execute with local resource
                    result = await self._execute_with_resource(task, local_resource)
                else:
                    # Request resources from Gateway Agents
                    resources = await self.request_resources(task)
                    
                    if resources:
                        # Select best resource and execute
                        selected_resource = resources[0]
                        task.assigned_resource = selected_resource.id
                        
                        # Use A2A protocol for agent communication
                        if self.a2a_protocol:
                            result = await self.a2a_protocol.invoke_agent(
                                selected_resource.endpoint,
                                task.description,
                                task.context
                            )
                        else:
                            result = await self._execute_with_resource(task, selected_resource)
                    else:
                        result = {"error": "No suitable resources found"}
                
                task.result = result
                task.status = "completed"
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error executing task {task.id}: {e}")
                task.status = "failed"
                task.result = {"error": str(e)}
                results.append(task.result)
        
        # Store in execution history
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "request": user_request,
            "tasks": [t.__dict__ for t in tasks],
            "results": results
        }
        self.execution_history.append(execution_record)
        
        return {
            "request": user_request,
            "tasks_executed": len(tasks),
            "results": results,
            "mode": self.mode.value
        }
    
    def _find_local_resource(self, requirements: List[str]) -> Optional[Resource]:
        """Check local resource pool for suitable resource"""
        for resource_id, resource in self.local_resources.items():
            if any(req in resource.capabilities for req in requirements):
                return resource
        return None
    
    async def _execute_with_resource(self, task: Task, resource: Resource) -> Dict[str, Any]:
        """Execute task with selected resource"""
        logger.info(f"Executing task {task.id} with resource {resource.name}")
        
        # In production, this would make actual API calls
        # For MVP, simulating execution
        await asyncio.sleep(0.1)  # Simulate processing time
        
        return {
            "task_id": task.id,
            "resource_used": resource.name,
            "status": "success",
            "result": f"Executed '{task.description}' using {resource.name}"
        }
    
    async def _reasoning_react(self, task: Task, observation: Any):
        """ReAct reasoning strategy - Reason, Act, Observe cycle"""
        # Implement ReAct strategy
        logger.debug("Using ReAct reasoning strategy")
        # This would integrate with LLM for actual reasoning
        pass
    
    async def _reasoning_rewoo(self, task: Task):
        """ReWOO reasoning strategy - Reasoning Without Observation"""
        # Implement ReWOO strategy
        logger.debug("Using ReWOO reasoning strategy")
        pass
    
    async def _reasoning_tree_of_thoughts(self, task: Task):
        """Tree of Thoughts reasoning strategy"""
        # Implement ToT strategy
        logger.debug("Using Tree of Thoughts reasoning strategy")
        pass
    
    def set_operation_mode(self, mode: OperationMode):
        """Switch operation mode"""
        self.mode = mode
        logger.info(f"Operation mode changed to: {mode.value}")
    
    def get_execution_history(self) -> List[Dict]:
        """Get task execution history"""
        return self.execution_history
    
    def get_context(self) -> Dict:
        """Get current context"""
        return self.context