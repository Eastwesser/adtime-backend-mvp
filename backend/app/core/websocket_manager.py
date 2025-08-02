from typing import Dict

from fastapi import WebSocket


class ConnectionManager:
    """Менеджер WebSocket-подключений для чата по заказам"""

    def __init__(self):
        # Формат: {order_id: [WebSocket1, WebSocket2]}
        self.active_connections: Dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, order_id: str):
        await websocket.accept()
        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
        self.active_connections[order_id].append(websocket)

    def disconnect(self, websocket: WebSocket, order_id: str):
        if order_id in self.active_connections:
            self.active_connections[order_id].remove(websocket)
            if not self.active_connections[order_id]:
                del self.active_connections[order_id]

    async def broadcast(self, message: str, order_id: str):
        """Отправить сообщение всем участникам чата заказа"""
        if order_id in self.active_connections:
            for connection in self.active_connections[order_id]:
                await connection.send_text(message)


# Глобальный экземпляр менеджера
ws_manager = ConnectionManager()
