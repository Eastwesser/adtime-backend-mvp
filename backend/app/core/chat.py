from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends

from app.core.websocket_manager import ws_manager
from app.repositories import OrderRepository

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.websocket("/orders/{order_id}")
async def websocket_chat(
        websocket: WebSocket,
        order_id: str,
        order_repo: OrderRepository = Depends()
):
    # Проверяем существование заказа
    if not await order_repo.exists(order_id):
        await websocket.close(code=1008)
        return

    await ws_manager.connect(websocket, order_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Здесь логика сохранения сообщения в БД
            await ws_manager.broadcast(data, order_id)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, order_id)
