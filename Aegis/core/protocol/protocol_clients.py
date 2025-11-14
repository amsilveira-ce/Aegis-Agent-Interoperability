import asyncio
import logging
import httpx
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


# ============================================================================
# A2A PROTOCOL CLIENT 
# ============================================================================
class A2AProtocolClient:

    def __init__(self, client_id: str = None):
        self.client_id = client_id or f"principal-agent-{id(self)}"
        self.session = None
        self._connected_agents: Dict[str, Dict] = {}

        logger.info(f"A2A Protocol Client initialized: {self.client_id}")


    async def connect(self) -> bool:
        """Initialize A2A client connection"""
        try:
            
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                limits=httpx.Limits(max_keepalive_connections=10)
            )
            logger.info("A2A client connected")

            return True
        
        except Exception as e:
            logger.error(f"Failed to connect A2A client: {e}")
            return False
        
    async def invoke_agent(
            self, 
            endpoint: str, 
            task_desc: str, 
            context: Dict[str, Any]) -> Dict[str, Any]:
        

        try:
            logger.info(f"A2A: Invoking agent at {endpoint} for task: '{task_desc}'")

            # Current implementation using A2A protocol structure - can be replaced for the oficial sdk later 
            request_payload = {
                    "jsonrpc": "2.0",
                    "method": "agent.invoke",
                    "params": {
                        "task": {
                            "description": task_desc,
                            "context": context,
                            "requester_id": self.client_id
                        }
                    },
                    "id": f"req_{id(self)}_{asyncio.get_event_loop().time()}"
            }

            response = await self.session.post(
                    f"{endpoint}/a2a/invoke",
                    json=request_payload,

                    headers={
                        "Content-Type": "application/json",
                        "X-A2A-Client-ID": self.client_id
                    }
            )

            response.raise_for_status()
            result = response.json()

            if "error" in result:
                logger.error(f"A2A invocation error: {result['error']}")
                return {"error": result["error"]}
            
            return result.get("result", {})
        
        except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error invoking agent: {e.response.status_code}")
                return {"error": f"HTTP {e.response.status_code}"}
        
        except Exception as e:
            logger.error(f"Failed to invoke agent at {endpoint}: {e}")
            return {"error": str(e)}
    
    async def discover_agent(self, endpoint: str):
        """
        Discover an agent's capabilities via A2A protocol.
        
        Args:
            endpoint: Agent's A2A endpoint
            
        Returns:
            Agent card with capabilities
        """
        try:
            
            # For now, using HTTP with A2A protocol structure
            response = await self.session.get(
               
                f"{endpoint}/a2a/agent-card",
                headers={"Accept": "application/json"}
            )
            
            if response.status_code == 200:
                agent_card = response.json()
                self._connected_agents[endpoint] = agent_card
                logger.info(f"Discovered agent at {endpoint}: {agent_card.get('name')}")
                return agent_card
            else:
                logger.warning(f"Failed to discover agent at {endpoint}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error discovering agent at {endpoint}: {e}")
            return None

    async def disconnect(self):
        """Disconnect A2A client"""
        if self.session:
            await self.session.aclose()
        logger.info("A2A client disconnected")





class MCPClient:

    def __init__(self):
        pass 

    async def invoke_tool(
            self, 
            endpoint: str, 
            tool_name: str=None,
            params: Dict[str, Any] = None) -> Dict[str,Any]:
        
        pass


class UnifiedProtocolClient:
    """
    Unified client that automatically selects the appropriate protocol.
    Provides a single interface for both A2A and MCP communication.
    """
    def __init__(self):
        self.a2a_client = A2AProtocolClient()
        self.mcp_client = MCPClient()
        self._connected = False

    async def connect(self) -> bool:
        """Connect both protocol clients"""
        try:
            a2a_connected = await self.a2a_client.connect()
            mcp_connected = await self.mcp_client.connect()
            self._connected = a2a_connected and mcp_connected
            return self._connected
        except Exception as e:
            logger.error(f"Failed to connect unified client: {e}")
            return False
        
    async def invoke(self, 
                    endpoint: str,
                    resource_type: str,
                    task_desc: str = None,
                    params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Invoke a resource using the appropriate protocol.
        
        Args:
            endpoint: Resource endpoint
            resource_type: "agent" or "tool"
            task_desc: Task description (for agents)
            params: Parameters/context
            
        Returns:
            Execution result
        """
        if not self._connected:
            await self.connect()
        
        if resource_type == "agent":
            # Use A2A for agent communication
            return await self.a2a_client.invoke_agent(
                endpoint=endpoint,
                task_desc=task_desc or "Execute task",
                context=params or {}
            )
        elif resource_type == "tool":
            # Use MCP for tool invocation
            return await self.mcp_client.invoke_tool(
                endpoint=endpoint,
                params=params
            )
        else:
            logger.error(f"Unknown resource type: {resource_type}")
            return {"error": f"Unknown resource type: {resource_type}"}   

def create_protocol_client(protocol_type: str = "unified") -> Any:
    """
    Factory function to create protocol clients.
    
    Args:
        protocol_type: "a2a", "mcp", or "unified"
        
    Returns:
        Protocol client instance
    """
    if protocol_type == "a2a":
        return A2AProtocolClient()
    elif protocol_type == "mcp":
        return MCPClient()
    elif protocol_type == "unified":
        return UnifiedProtocolClient()
    else:
        raise ValueError(f"Unknown protocol type: {protocol_type}")