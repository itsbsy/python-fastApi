from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
import asyncio

app = FastAPI()

# List to store connected clients
connected_clients: List[WebSocket] = []

# WebSocket endpoint to handle SSE
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            # This is just an example. In a real scenario, you might have a more sophisticated logic to send updates.
            message = "Message from server"
            await websocket.send_text(message)
            await asyncio.sleep(5) 
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# Example API endpoint to send a message to all connected clients
@app.get("/send_message/{message}")
async def send_message(message: str):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except WebSocketDisconnect:
            connected_clients.remove(client)
    return {"message": "Message sent to all clients"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
