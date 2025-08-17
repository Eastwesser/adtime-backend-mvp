from typing import Callable, Awaitable
from fastapi import BackgroundTasks

class WebhookManager:
    def __init__(self):
        self._handlers = []

    def register(self, event_type: str):
        def decorator(handler: Callable[[dict], Awaitable[None]]):
            self._handlers.append((event_type, handler))
            return handler
        return decorator

    async def trigger(self, event_type: str, payload: dict, background_tasks: BackgroundTasks):
        for handler_type, handler in self._handlers:
            if handler_type == event_type:
                background_tasks.add_task(handler, payload)

# Global instance
webhook_manager = WebhookManager()