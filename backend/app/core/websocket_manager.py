import logging
from datetime import datetime
from typing import Dict, List
from uuid import UUID

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Расширенный менеджер WebSocket-подключений с:
    - Ограничением подключений
    - Логированием
    - Сохранением истории
    - Обработкой ошибок

    Пример использования:
         manager = ConnectionManager()
         await manager.connect(websocket, "order_id")
         await manager.broadcast("order_id", "message")
    """

    def __init__(self, max_connections: int = 100):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.connection_count = 0
        self.max_connections = max_connections
        self.message_history: Dict[str, List[dict]] = {}

    async def connect(self, websocket: WebSocket, order_id: str):
        """Подключение нового клиента с валидацией"""
        if self.connection_count >= self.max_connections:
            logger.warning(f"Connection limit reached for order {order_id}")
            raise WebSocketDisconnect(
                code=1008,  # Policy Violation
                reason="Maximum connections reached"
            )

        await websocket.accept()
        self.connection_count += 1

        if order_id not in self.active_connections:
            self.active_connections[order_id] = []
            self.message_history[order_id] = []

        self.active_connections[order_id].append(websocket)
        logger.info(f"New connection for order {order_id}. Total: {self.connection_count}")

    def disconnect(self, websocket: WebSocket, order_id: str):
        """Отключение клиента с очисткой"""
        if order_id in self.active_connections:
            self.active_connections[order_id].remove(websocket)
            self.connection_count -= 1

            if not self.active_connections[order_id]:
                del self.active_connections[order_id]
                logger.info(f"Last connection closed for order {order_id}")

    async def broadcast(self, order_id: str, message: str, sender: UUID = None):
        """
        Отправка сообщения всем участникам чата
        с сохранением в истории и обработкой ошибок
        """
        if order_id not in self.active_connections:
            logger.warning(f"No active connections for order {order_id}")
            return

        # Сохраняем сообщение в истории
        msg_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "sender": str(sender) if sender else "system",
            "message": message
        }
        self.message_history[order_id].append(msg_data)

        # Отправляем всем подключенным клиентам
        for connection in self.active_connections[order_id]:
            try:
                await connection.send_json(msg_data)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                self.disconnect(connection, order_id)

    def get_history(self, order_id: str, limit: int = 50) -> List[dict]:
        """Получение истории сообщений для заказа"""
        return self.message_history.get(order_id, [])[-limit:]


# Глобальный экземпляр с настройками из конфига
ws_manager = ConnectionManager(max_connections=200)
