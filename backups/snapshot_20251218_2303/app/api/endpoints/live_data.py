from fastapi import APIRouter, WebSocket
from app.services.live_data import LiveDataFeed

router = APIRouter()
live_feed = LiveDataFeed()

@router.websocket("/ws/live-data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await live_feed.register(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Optionally process incoming messages
    finally:
        await live_feed.unregister(websocket) 