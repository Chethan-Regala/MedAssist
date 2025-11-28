from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional
from uuid import uuid4

from app.utils import configure_logging


class AgentMessage:
    """Message format for agent-to-agent communication."""
    
    def __init__(self, sender: str, receiver: str, message_type: str, payload: Dict[str, Any]):
        self.id = str(uuid4())[:8]
        self.sender = sender
        self.receiver = receiver
        self.message_type = message_type
        self.payload = payload
        self.timestamp = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "type": self.message_type,
            "payload": self.payload,
            "timestamp": self.timestamp
        }


class A2AProtocol:
    """Agent-to-Agent communication protocol."""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.message_queue: List[AgentMessage] = []
        self.logger = configure_logging()
    
    def register_agent(self, agent_id: str, agent_instance: Any):
        """Register an agent for A2A communication."""
        self.agents[agent_id] = agent_instance
        self.logger.info(f"Agent {agent_id} registered for A2A communication")
    
    async def send_message(self, message: AgentMessage) -> bool:
        """Send message between agents."""
        if message.receiver not in self.agents:
            self.logger.error(f"Receiver agent {message.receiver} not found")
            return False
        
        self.message_queue.append(message)
        self.logger.info(f"Message {message.id} queued: {message.sender} -> {message.receiver}")
        
        # Process message immediately
        return await self._process_message(message)
    
    async def _process_message(self, message: AgentMessage) -> bool:
        """Process agent message."""
        try:
            receiver_agent = self.agents[message.receiver]
            
            # Handle different message types
            if message.message_type == "health_consultation":
                result = await self._handle_consultation(receiver_agent, message.payload)
            elif message.message_type == "medication_review":
                result = await self._handle_medication_review(receiver_agent, message.payload)
            else:
                self.logger.warning(f"Unknown message type: {message.message_type}")
                return False
            
            self.logger.info(f"Message {message.id} processed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process message {message.id}: {e}")
            return False
    
    async def _handle_consultation(self, agent: Any, payload: Dict[str, Any]) -> Any:
        """Handle health consultation between agents."""
        if hasattr(agent, 'run'):
            return await agent.run(payload)
        return None
    
    async def _handle_medication_review(self, agent: Any, payload: Dict[str, Any]) -> Any:
        """Handle medication review between agents."""
        if hasattr(agent, 'run'):
            return await agent.run(payload)
        return None
    
    def get_message_history(self) -> List[Dict[str, Any]]:
        """Get A2A message history."""
        return [msg.to_dict() for msg in self.message_queue]


# Global A2A protocol instance
a2a_protocol = A2AProtocol()