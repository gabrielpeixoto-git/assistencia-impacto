from typing import Dict, Set
from fastapi import WebSocket
from loguru import logger
import json


class ConnectionManager:
    """Gerenciador de conexões WebSocket para notificações em tempo real."""
    
    def __init__(self):
        # Armazena conexões ativas por usuário
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Armazena conexões por tipo de notificação
        self.subscriptions: Dict[str, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Conecta um novo usuário."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        logger.info(f"Usuário {user_id} conectado via WebSocket")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Desconecta um usuário."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            # Remove usuário se não tiver mais conexões
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        # Remove subscriptions
        for notification_type, users in self.subscriptions.items():
            users.discard(user_id)
        
        logger.info(f"Usuário {user_id} desconectado do WebSocket")
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Envia mensagem para um usuário específico."""
        if user_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Erro ao enviar mensagem para usuário {user_id}: {str(e)}")
                    disconnected.add(connection)
            
            # Remove conexões desconectadas
            for connection in disconnected:
                self.active_connections[user_id].discard(connection)
    
    async def broadcast(self, message: dict, notification_type: str = None):
        """Envia mensagem para todos os usuários inscritos em um tipo de notificação."""
        if notification_type and notification_type in self.subscriptions:
            for user_id in self.subscriptions[notification_type]:
                await self.send_personal_message(message, user_id)
    
    def subscribe(self, user_id: str, notification_type: str):
        """Inscreve usuário em um tipo de notificação."""
        if notification_type not in self.subscriptions:
            self.subscriptions[notification_type] = set()
        
        self.subscriptions[notification_type].add(user_id)
        logger.info(f"Usuário {user_id} inscrito em {notification_type}")
    
    def unsubscribe(self, user_id: str, notification_type: str):
        """Desinscreve usuário de um tipo de notificação."""
        if notification_type in self.subscriptions:
            self.subscriptions[notification_type].discard(user_id)
            logger.info(f"Usuário {user_id} desinscrito de {notification_type}")
    
    def get_connected_users(self) -> Set[str]:
        """Retorna lista de usuários conectados."""
        return set(self.active_connections.keys())
    
    def is_user_connected(self, user_id: str) -> bool:
        """Verifica se usuário está conectado."""
        return user_id in self.active_connections


# Instância global do gerenciador
manager = ConnectionManager()
