from fastapi import FastAPI, Request
from app.line_api import reply_message, get_user_profile, send_quiz, send_score_card
from app.scores import update_or_add_user_score, reset_user_score
from app.quiz import get_random_question, record_question_history
from dotenv import load_dotenv
import os
import json

load_dotenv()
app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print(json.dumps(body, indent=2))

    for event in body["events"]:
        user_id = event["source"]["userId"]
        profile = get_user_profile(user_id)
        name = profile.get("displayName", "user")

        if event["type"] == "message":
            text = event["message"]["text"].lower()
            if "เริ่ม" in text or "quiz" in text:
                send_quiz(user_id)
            elif "รีเซต" in text:
                reset_user_score(user_id)
                reply_message(user_id, "✅ คุณได้รีเซตคะแนนแล้วครับ ✨")       
            elif text == "ดูคะแนน":
                send_score_card(user_id)
            else:
                reply_message(user_id, "พิมพ์ 'เริ่ม' เพื่อเริ่มทำแบบทดสอบ 🤖")

        elif event["type"] == "postback":
            try:
                data = event["postback"]["data"]
                params = dict(item.split("=") for item in data.split("|"))

                answer = params.get("answer", "").strip()
                correct = params.get("correct", "").strip()
                question = params.get("question", "").strip()

                if not answer or not correct or not question:
                    raise ValueError("Missing data in postback")

                is_correct = answer == correct
                score = update_or_add_user_score(user_id, name, is_correct)

                record_question_history(user_id, question)

                if is_correct:
                    reply_message(user_id, f"✅ ถูกต้อง! คุณได้ 10 คะแนน (รวม {score} คะแนน)")
                else:
                    reply_message(user_id, f"❌ คำตอบที่ถูกคือ: {correct}\nคะแนนคุณคือ {score}")

                send_quiz(user_id)

            except Exception as e:
                print("⚠️ ERROR handling postback:", e)
                reply_message(user_id, "เกิดข้อผิดพลาดในการประมวลผลคำตอบ")
       
    return {"status": "ok"}