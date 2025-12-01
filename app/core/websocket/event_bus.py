import asyncio
import logging
from typing import Dict,Any

logger = logging.getLogger(__name__)

class MemoryBus:
    """
        Pattern: Event Bus (Producer-Consumer).
        Implementation: Simple in-memory queue using asyncio.Queue.
        Purpose: Decouples the WebSocket Handler (Producer) from the AI Agent (Consumer).
    """
    def __init__(self):
        # The queue holding messages destined for the AI Agent
        self.ai_queue = asyncio.Queue()

    """Method used by the Producer (WS Handler) to put a message on the queue."""
    async def publish_to_ia(self, event: Dict[str, Any]):
        logger.info(f"Publishing event to bus: {event.get('type')}")
        await self.ai_queue.put(event)
        
    """Method used by the Consumer (AI Agent) to retrieve the next message."""
    async def consume_ai_event(self):
        # Blocks until an item is available
        return await self.ai_queue.get()
    
# Global Instance (Singleton Pattern)
event_bus = MemoryBus()