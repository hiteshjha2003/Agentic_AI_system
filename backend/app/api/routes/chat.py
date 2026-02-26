# backend/app/api/routes/chat.py
from fastapi import APIRouter, WebSocket

router = APIRouter(tags=["chat"])

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Implementation same as in main.py
    pass