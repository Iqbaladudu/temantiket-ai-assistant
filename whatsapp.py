import json

import requests


async def get_message(message):
    msg = json.loads(message)
    for typs in msg:
        if msg[typs] == "message":
            chat_id = msg["payload"]["from"]
            chat_body = msg["payload"]["body"]
            return chat_id, chat_body

async def send_message(chat_id, chat_body):
    result = requests.post("http://localhost:3000/api/sendText", json={
  "chatId": chat_id,
  "reply_to": chat_id,
  "text": chat_body,
  "linkPreview": True,
  "session": "default"
    }, headers={
        "Content-Type": "application/json"
    })

    return result