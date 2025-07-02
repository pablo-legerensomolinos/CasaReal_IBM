from fastapi import WebSocket
from uuid import uuid4

from .Singleton import Singleton
from fastapi_template.Logger import Logger

from fastapi_template.env import LogConfig

# use this info on the other websockets


class WebSocketManager(metaclass=Singleton):
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.logger = Logger('websocket_logger', LogConfig.misc_level).logger
        self.logger.info("WebSocket Manager successfully initialized.")

    async def connect(self, websocket: WebSocket):
        websocket_id = str(uuid4())
        await websocket.accept()
        self.active_connections[websocket_id] = websocket
        return websocket_id

    async def disconnect(self, websocket_id: str):
        self.active_connections.pop(websocket_id, None)

    async def close(self, websocket_id: str):
        self.active_connections[websocket_id].close()
        self.disconnect(websocket_id)

    async def send_text(self, message: str, websocket_id: str):
        try:
            await self.active_connections[websocket_id].send_text(message)
        except:
            print("Cannot send")

    async def send_json(self, message: str, websocket_id: str):
        try:
            await self.active_connections[websocket_id].send_json(message)
        except:
            print("Cannot send")

    async def send_bytes(self, message: str, websocket_id: str):
        try:
            await self.active_connections[websocket_id].send_bytes(message)
        except:
            print("Cannot send")

    async def broadcast_text(self, message: str):
        for connection in self.active_connections.values():
            try:
                await connection.send_text(message)
            except:
                print("Cannot send")
