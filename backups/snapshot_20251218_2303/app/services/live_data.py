import asyncio
import websockets
import json

class LiveDataFeed:
    def __init__(self):
        self.clients = set()

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)

    async def broadcast(self, message):
        if self.clients:
            await asyncio.wait([client.send(json.dumps(message)) for client in self.clients])

    async def handler(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                # Echo or process messages if needed
                pass
        finally:
            await self.unregister(websocket) 