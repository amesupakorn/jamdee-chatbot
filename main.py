from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
import os, json

from app.line_api import reply_message, get_user_profile, send_quiz, send_math_question, send_score_card, send_game_menu
from app.scores import update_or_add_user_score, reset_user_score
from app.quiz import record_question_history
from app.quizMath import record_math_history

load_dotenv()
app = FastAPI()
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    print(json.dumps(body, indent=2))

    for event in body["events"]:
        user_id = event["source"]["userId"]

        # ✅ ส่วนนี้คงไว้ ไม่เปลี่ยน
        if event["type"] == "message":
            text = event["message"]["text"].lower()
            if "รีเซต" in text:
                reset_user_score(user_id)
                reply_message(user_id, "✅ คุณได้รีเซตคะแนนแล้วครับ ✨")       
            elif text == "ดูคะแนน":
                send_score_card(user_id)
            elif "เล่นเกมฝึกสมอง" in text:
                send_game_menu(user_id)
            elif "เริ่มเกมบวกเลข" in text:
                send_math_question(user_id)
            elif "เริ่ม" in text or "quiz" in text:
                send_quiz(user_id)
            else:
                reply_message(user_id, "พิมพ์ 'เริ่ม' เพื่อเริ่มทำแบบทดสอบ 🤖")

        # ✅ ส่วนนี้ทำให้เร็วขึ้นด้วย background task
        elif event["type"] == "postback":
            background_tasks.add_task(handle_postback_event, event)

    return {"status": "ok"}


def handle_postback_event(event):
    try:
        user_id = event["source"]["userId"]
        profile = get_user_profile(user_id)
        name = profile.get("displayName", "ผู้ใช้")

        data = event["postback"]["data"]
        params = dict(item.split("=", 1) for item in data.split("|") if "=" in item)

        answer = params.get("answer")
        correct = params.get("correct")
        question = params.get("question")
        mode = params.get("mode", "quiz")

        if None in [answer, correct, question]:
            raise ValueError("Missing data in postback")

        is_correct = answer.strip() == correct.strip()
        score = update_or_add_user_score(user_id, name, is_correct)

        # 🔒 บันทึกหลังตอบ
        if mode == "math":
            record_math_history(user_id, question)
        else:
            record_question_history(user_id, question)

        feedback = (
            f"✅ ถูกต้อง! คุณได้ 10 คะแนน (รวม {score} คะแนน)"
            if is_correct else
            f"❌ คำตอบที่ถูกคือ: {correct}\nคะแนนคุณคือ {score}"
        )
        reply_message(user_id, feedback)

        # 🔁 ส่งคำถามถัดไป
        if mode == "math":
            send_math_question(user_id)
        else:
            send_quiz(user_id)

    except Exception as e:
        print(f"⚠️ ERROR handling postback: {e}")