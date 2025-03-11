import asyncio

import websockets

from temantiket_assistant import stream_graph_updates
from whatsapp import get_message, send_message

WEBSOCKET_URI = "ws://localhost:3000/ws?session=default&events=message"


class WebSocketClient:
    def __init__(self):
        self.websocket = None
        self.running = False

    async def connect(self):
        while True:
            try:
                async with websockets.connect(WEBSOCKET_URI) as websocket:
                    self.websocket = websocket
                    self.running = True
                    print("Connected to WebSocket server")
                    await self.receive_messages()
            except Exception as e:
                print(f"WebSocket connection failed: {e}")
                self.running = False
                await asyncio.sleep(5)

    async def receive_messages(self):
        try:
            while self.running:
                message = await self.websocket.recv()
                chat_id, chat_body, session_id = await get_message(message)
                assistant = stream_graph_updates(chat_body, session_id)
                # processed_msg = await self.agent.process_message(session_id, messages=chat_body)
                await send_message(chat_id, assistant)


        except Exception as e:
            print(f"WebSocket error: {e}")
            self.running = False

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            self.running = False
ws_client = WebSocketClient()