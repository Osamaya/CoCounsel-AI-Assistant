from typing import Dict,Set
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class SubscriptionManager:
    """
    Gestor centralizado de los datos de suscripción a canales.
    En una aplicación real, esta data vendría de la base de datos.
    """
    # CLAVE: Mapeo de channel_name -> Set[user_id]
    _channel_subscriptions: Dict[str, Set[str]] = {
        # MOCK DATA: Simulación de usuarios suscritos a canales, si cambiamos el id no deberiamos de recibir nada
        "chat": {1}, # Todos
    }
    
    @classmethod
    def get_users_for_channel(cls, channel: str) -> Set[str]:
        """Devuelve el conjunto de user_ids suscritos a un canal."""
        return cls._channel_subscriptions.get(channel, set())
        
    @classmethod
    def add_subscription(cls, channel: str, user_id: str):
        """Mock: Simula añadir un usuario a una suscripción."""
        if channel not in cls._channel_subscriptions:
             cls._channel_subscriptions[channel] = set()
        cls._channel_subscriptions[channel].add(user_id)
        logger.info(f"➕ Suscripción añadida: {user_id} -> {channel}")

# Inicializamos el gestor
subscription_manager = SubscriptionManager()