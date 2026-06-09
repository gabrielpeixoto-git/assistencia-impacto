from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.websocket.manager import manager
from app.core.seguranca import verificar_token
from loguru import logger
from typing import Optional


router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    notification_types: Optional[str] = None
):
    """Endpoint WebSocket para notificações em tempo real."""
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    # Aceitar a conexão PRIMEIRO (obrigatório antes de qualquer validação)
    await websocket.accept()
    
    try:
        # Validar token e obter usuário
        payload = verificar_token(token)
        if payload is None:
            logger.warning(f"Tentativa de conexão WebSocket rejeitada: token inválido (IP: {client_ip})")
            await websocket.send_json({"tipo": "erro", "mensagem": "Token inválido"})
            await websocket.close(code=4001, reason="Invalid token")
            return
        user_id = payload.get("sub")
        
        # Conectar usuário
        await manager.connect(websocket, user_id)
        logger.info(f"WebSocket conectado: usuário {user_id} (IP: {client_ip})")
        
        # Inscrever em tipos de notificação se especificados
        if notification_types:
            for notification_type in notification_types.split(","):
                manager.subscribe(user_id, notification_type.strip())
        
        # Manter conexão aberta e receber mensagens
        while True:
            data = await websocket.receive_json()
            
            # Processar mensagem recebida do cliente
            message_type = data.get("type")
            
            if message_type == "subscribe":
                # Inscrever em tipo de notificação
                notification_type = data.get("notification_type")
                if notification_type:
                    manager.subscribe(user_id, notification_type)
            
            elif message_type == "unsubscribe":
                # Desinscrever de tipo de notificação
                notification_type = data.get("notification_type")
                if notification_type:
                    manager.unsubscribe(user_id, notification_type)
            
            elif message_type == "ping":
                # Responder ping
                await websocket.send_json({"type": "pong"})
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket desconectado: usuário {user_id} (IP: {client_ip})")
    
    except Exception as e:
        logger.error(f"Erro no WebSocket para usuário {user_id} (IP: {client_ip}): {str(e)}")
        manager.disconnect(websocket, user_id)


@router.websocket("/ws/{user_id}")
async def websocket_user_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str = Query(...)
):
    """Endpoint WebSocket específico para um usuário."""
    client_ip = websocket.client.host if websocket.client else "unknown"
    
    # Aceitar a conexão PRIMEIRO (obrigatório antes de qualquer validação)
    await websocket.accept()
    
    try:
        # Validar token e verificar se corresponde ao usuário
        payload = verificar_token(token)
        if payload is None:
            logger.warning(f"Tentativa de conexão WebSocket rejeitada: token inválido (IP: {client_ip})")
            await websocket.send_json({"tipo": "erro", "mensagem": "Token inválido"})
            await websocket.close(code=4001, reason="Invalid token")
            return
        
        if payload.get("sub") != user_id:
            logger.warning(f"Tentativa de conexão WebSocket rejeitada: token não corresponde ao usuário {user_id} (IP: {client_ip})")
            await websocket.close(code=4003, reason="Unauthorized")
            return
        
        # Conectar usuário
        await manager.connect(websocket, user_id)
        logger.info(f"WebSocket conectado: usuário {user_id} (IP: {client_ip})")
        
        # Manter conexão aberta
        while True:
            await websocket.receive_json()
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
        logger.info(f"WebSocket desconectado: usuário {user_id} (IP: {client_ip})")
    
    except Exception as e:
        logger.error(f"Erro no WebSocket para usuário {user_id} (IP: {client_ip}): {str(e)}")
        manager.disconnect(websocket, user_id)
