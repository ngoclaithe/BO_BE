from typing import Dict
from fastapi import WebSocket
from enum import Enum

class ClientType(Enum):
    ADMIN = "admin"
    FE = "fe"

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Dict[str, WebSocket]] = {
            ClientType.ADMIN.value: {},
            ClientType.FE.value: {}
        }

    async def connect(self, websocket: WebSocket, client_type: str, client_id: int):
        await websocket.accept()
        if client_type not in self.connections:
            self.connections[client_type] = {}
        self.connections[client_type][str(client_id)] = websocket

    def disconnect(self, client_type: str, client_id: int):
        if str(client_id) in self.connections[client_type]:
            del self.connections[client_type][str(client_id)]

    async def send_to_admin(self, client_id: str, message: str):
        if client_id in self.connections[ClientType.ADMIN.value]:
            websocket = self.connections[ClientType.ADMIN.value][client_id]
            await websocket.send_text(message)

    async def send_to_fe(self, client_id: str, message: str):
        if client_id in self.connections[ClientType.FE.value]:
            websocket = self.connections[ClientType.FE.value][client_id]
            await websocket.send_text(message)

    async def broadcast_to_admin(self, message: str):
        if not self.connections[ClientType.ADMIN.value]:
            print("No admin clients connected. Skipping broadcast.") 
            return

        print(f"Broadcasting to all admin clients: {message}")  
        for websocket in self.connections[ClientType.ADMIN.value].values():
            try:
                await websocket.send_text(message)
            except Exception as e:
                print(f"Error sending message to admin: {e}") 

    async def broadcast_to_fe(self, message: str):
        for websocket in self.connections[ClientType.FE.value].values():
            await websocket.send_text(message)