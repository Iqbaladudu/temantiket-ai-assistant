import asyncio
import os

import websockets
from dotenv import load_dotenv

from temantiket_assistant import stream_graph_updates
from whatsapp import get_message, send_message

load_dotenv()


class WebSocketClient:
    def __init__(self):
        self.websocket = None
        self.running = False

    async def connect(self):
        while True:
            try:
                async with websockets.connect(os.environ.get("WEBSOCKET_URI")) as websocket:
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
                chat_id, chat_body = await get_message(message)
                assistant = stream_graph_updates(chat_body, chat_id)
                await send_message(chat_id, assistant)


        except Exception as e:
            print(f"WebSocket error: {e}")
            self.running = False

    async def close(self):
        if self.websocket:
            await self.websocket.close()
            self.running = False
ws_client = WebSocketClient()