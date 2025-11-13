"""
Agent-to-Agent Communication System for B3PersonalAssistant.

Provides robust messaging infrastructure for inter-agent coordination,
collaboration, and self-improvement workflows.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from queue import Queue, Empty
from threading import Lock
import json

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of inter-agent messages."""
    REQUEST = "request"          # Request for information/action
    RESPONSE = "response"        # Response to a request
    BROADCAST = "broadcast"      # Message to all agents
    NOTIFICATION = "notification"  # Status update
    DELEGATION = "delegation"    # Task delegation
    COLLABORATION = "collaboration"  # Collaborative work request
    FEEDBACK = "feedback"        # Feedback on performance
    IMPROVEMENT = "improvement"  # Improvement suggestion


class MessagePriority(Enum):
    """Priority levels for messages."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class AgentMessage:
    """Message sent between agents."""
    message_id: str
    message_type: MessageType
    from_agent: str
    to_agent: str
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    requires_response: bool = False
    response_to: Optional[str] = None  # ID of message being responded to
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'from_agent': self.from_agent,
            'to_agent': self.to_agent,
            'content': self.content,
            'context': self.context,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'requires_response': self.requires_response,
            'response_to': self.response_to,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentMessage':
        """Create message from dictionary."""
        return cls(
            message_id=data['message_id'],
            message_type=MessageType(data['message_type']),
            from_agent=data['from_agent'],
            to_agent=data['to_agent'],
            content=data['content'],
            context=data.get('context', {}),
            priority=MessagePriority(data.get('priority', 1)),
            timestamp=data.get('timestamp', time.time()),
            requires_response=data.get('requires_response', False),
            response_to=data.get('response_to'),
            metadata=data.get('metadata', {})
        )


class MessageBroker:
    """
    Central message broker for agent communication.

    Manages message queues, routing, and delivery between agents.
    Provides pub/sub pattern for broadcasts and point-to-point for direct messages.
    """

    def __init__(self):
        """Initialize the message broker."""
        self.logger = logging.getLogger("message_broker")
        self.agent_queues: Dict[str, Queue] = {}
        self.message_handlers: Dict[str, List[Callable]] = {}
        self.message_history: List[AgentMessage] = []
        self.max_history_size = 1000
        self.lock = Lock()
        self._message_counter = 0

        self.logger.info("Message broker initialized")

    def register_agent(self, agent_name: str, handler: Optional[Callable] = None):
        """
        Register an agent with the broker.

        Args:
            agent_name: Name of the agent
            handler: Optional message handler function
        """
        with self.lock:
            if agent_name not in self.agent_queues:
                self.agent_queues[agent_name] = Queue()
                self.message_handlers[agent_name] = []
                self.logger.info(f"Agent {agent_name} registered with message broker")

            if handler:
                self.message_handlers[agent_name].append(handler)
                self.logger.debug(f"Handler registered for {agent_name}")

    def send_message(self, message: AgentMessage) -> bool:
        """
        Send a message to an agent.

        Args:
            message: Message to send

        Returns:
            True if message was queued successfully
        """
        # Generate message ID if not set
        if not message.message_id:
            with self.lock:
                self._message_counter += 1
                message.message_id = f"msg_{message.from_agent}_{self._message_counter}_{int(time.time())}"

        # Check if target agent exists
        if message.to_agent not in self.agent_queues:
            if message.to_agent != "all":  # "all" is valid for broadcasts
                self.logger.warning(f"Target agent {message.to_agent} not registered")
                return False

        try:
            # Handle broadcasts
            if message.to_agent == "all":
                self._broadcast_message(message)
            else:
                # Queue message for specific agent
                self.agent_queues[message.to_agent].put(message)
                self.logger.debug(
                    f"Message {message.message_id} queued: "
                    f"{message.from_agent} → {message.to_agent} "
                    f"[{message.message_type.value}]"
                )

            # Store in history
            with self.lock:
                self.message_history.append(message)
                if len(self.message_history) > self.max_history_size:
                    self.message_history = self.message_history[-self.max_history_size:]

            return True

        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            return False

    def _broadcast_message(self, message: AgentMessage):
        """Broadcast message to all agents."""
        for agent_name in self.agent_queues.keys():
            if agent_name != message.from_agent:  # Don't send to sender
                broadcast_msg = AgentMessage(
                    message_id=f"{message.message_id}_to_{agent_name}",
                    message_type=message.message_type,
                    from_agent=message.from_agent,
                    to_agent=agent_name,
                    content=message.content,
                    context=message.context,
                    priority=message.priority,
                    metadata=message.metadata
                )
                self.agent_queues[agent_name].put(broadcast_msg)

        self.logger.info(f"Broadcast message {message.message_id} sent to all agents")

    def receive_message(self, agent_name: str, timeout: float = 0.1) -> Optional[AgentMessage]:
        """
        Receive a message for an agent.

        Args:
            agent_name: Name of the agent
            timeout: Timeout in seconds (0 for non-blocking)

        Returns:
            Message if available, None otherwise
        """
        if agent_name not in self.agent_queues:
            self.logger.warning(f"Agent {agent_name} not registered")
            return None

        try:
            message = self.agent_queues[agent_name].get(timeout=timeout)
            self.logger.debug(
                f"Message {message.message_id} received by {agent_name} "
                f"from {message.from_agent}"
            )
            return message
        except Empty:
            return None
        except Exception as e:
            self.logger.error(f"Error receiving message for {agent_name}: {e}")
            return None

    def get_pending_messages(self, agent_name: str) -> List[AgentMessage]:
        """
        Get all pending messages for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            List of pending messages
        """
        messages = []
        if agent_name not in self.agent_queues:
            return messages

        # Drain queue
        while True:
            try:
                msg = self.agent_queues[agent_name].get_nowait()
                messages.append(msg)
            except Empty:
                break

        # Re-queue messages (for now - in production you might want to mark as read)
        for msg in messages:
            self.agent_queues[agent_name].put(msg)

        return messages

    def get_message_history(
        self,
        agent_name: Optional[str] = None,
        message_type: Optional[MessageType] = None,
        limit: int = 50
    ) -> List[AgentMessage]:
        """
        Get message history with optional filtering.

        Args:
            agent_name: Filter by agent (from or to)
            message_type: Filter by message type
            limit: Maximum number of messages to return

        Returns:
            List of messages matching filters
        """
        with self.lock:
            messages = self.message_history[:]

        # Apply filters
        if agent_name:
            messages = [
                m for m in messages
                if m.from_agent == agent_name or m.to_agent == agent_name
            ]

        if message_type:
            messages = [m for m in messages if m.message_type == message_type]

        # Return most recent messages
        return messages[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get message broker statistics."""
        with self.lock:
            stats = {
                'registered_agents': len(self.agent_queues),
                'total_messages': len(self.message_history),
                'pending_by_agent': {
                    agent: queue.qsize()
                    for agent, queue in self.agent_queues.items()
                },
                'messages_by_type': {},
                'messages_by_agent': {}
            }

            # Count by type
            for msg in self.message_history:
                msg_type = msg.message_type.value
                stats['messages_by_type'][msg_type] = stats['messages_by_type'].get(msg_type, 0) + 1

                # Count by agent (sender)
                stats['messages_by_agent'][msg.from_agent] = stats['messages_by_agent'].get(msg.from_agent, 0) + 1

        return stats

    def clear_queue(self, agent_name: str):
        """Clear all messages for an agent."""
        if agent_name in self.agent_queues:
            with self.agent_queues[agent_name].mutex:
                self.agent_queues[agent_name].queue.clear()
            self.logger.info(f"Cleared message queue for {agent_name}")

    def clear_history(self):
        """Clear message history."""
        with self.lock:
            self.message_history.clear()
        self.logger.info("Message history cleared")


# Global message broker instance
_global_broker: Optional[MessageBroker] = None


def get_message_broker() -> MessageBroker:
    """Get or create the global message broker."""
    global _global_broker
    if _global_broker is None:
        _global_broker = MessageBroker()
    return _global_broker


def reset_message_broker():
    """Reset the global message broker (useful for testing)."""
    global _global_broker
    _global_broker = MessageBroker()
