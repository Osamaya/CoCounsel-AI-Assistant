import asyncio
import logging
from typing import Dict,Any

logger = logging.getLogger(__name__)

class MemoryBus:
    def __init__(self):
        #Cola donde formaremos los mensajes para nuestra IA
        self.ai_queue = asyncio.Queue()
        
    async def publish_to_ia(self, event: Dict[str, Any]):
        """Metemos el mensaje en la cola"""
        logger.info(f"Publicando evento al bus: {event.get('type')}")
        await self.ai_queue.put(event)
    
    async def consume_ai_event(self):
        """Scamos un mensaje de la cola"""
        return await self.ai_queue.get()
    
#Instancia global
event_bus = MemoryBus()