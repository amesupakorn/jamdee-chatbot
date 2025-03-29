from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

from utils.line_api import reply_message, get_user_profile
from utils.sheets import update_or_add_user_score

load_dotenv()
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    for event in body["events"]:
        if event["type"] == "postback":
            user_id = event["source"]["userId"]
            answer = event["postback"]["data"].split("=")[1]
            is_correct = answer == "tokyo"

            profile = get_user_profile(user_id)
            name = profile["displayName"] if profile else "unknown"

            update_or_add_user_score(user_id, name, is_correct)

            reply_message(user_id, f"{name} ได้รับ {10 if is_correct else 0} คะแนน!")
    return {"status": "ok"}