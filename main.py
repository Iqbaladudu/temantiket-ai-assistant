import asyncio
from typing import Union
from fastapi import FastAPI
from contextlib import asynccontextmanager
from langchain.chains import LLMChain

from temantiket_websocket import ws_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(ws_client.connect())
    try:
        yield
    finally:
        await ws_client.close()
        task.cancel()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}