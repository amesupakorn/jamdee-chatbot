from fastapi import FastAPI, Request, BackgroundTasks
from dotenv import load_dotenv
import os, json

from app.line_api import reply_message, get_user_profile, send_question, send_score_card, send_game_menu, start_loading_animation
from app.scores import update_or_add_user_score, reset_user_score
from app.quiz import get_answered_questions, record_question_history

load_dotenv()
app = FastAPI()

BOT_TOKENS = {
    "bot1": os.getenv("BOT1_ACCESS_TOKEN"),
    "bot2": os.getenv("BOT2_ACCESS_TOKEN")
}

@app.post("/webhook/{bot_id}")
async def webhook(bot_id: str, request: Request, background_tasks: BackgroundTasks):
    body = await request.json()
    print(f"💬 From bot: {bot_id}")
    token = BOT_TOKENS.get(bot_id)

    if not token:
        return {"status": "invalid bot id"}

    for event in body.get("events", []):
        user_id = event["source"]["userId"]

        if event["type"] == "message":
            text = event["message"]["text"].lower()
            start_loading_animation(user_id, token)

            if text == "ดูคะแนน":
                send_score_card(user_id, token)
            elif "เล่นเกม" in text or "เล่นเกมฝึกสมองง!" in text or "เล่นเกมฝึกสมอง" in text:
                send_game_menu(user_id, token)
            elif "เริ่มเกมคณิตศาสตร์" in text:
                send_question(user_id, key="math", token=token)
            elif "เริ่มเกมทายเงาสัตว์" in text:
                send_question(user_id, key="match", token=token)
            elif "เริ่มเกมทายสุภาษิต" in text:
                send_question(user_id, key="proverb", token=token)

        elif event["type"] == "postback":
            background_tasks.add_task(handle_postback_event, event, token)

    return {"status": "ok"}

processing_users = {}

def handle_postback_event(event, token):
    user_id = event["source"]["userId"]

    if processing_users.get(user_id):
        print("⏳ กำลังประมวลผลคำตอบก่อนหน้า")
        return
    try:
        processing_users[user_id] = True
        start_loading_animation(user_id, token=token)

        profile = get_user_profile(user_id, token=token)
        name = profile.get("displayName", "ผู้ใช้")

        data = event["postback"]["data"]
        params = dict(item.split("=", 1) for item in data.split("|") if "=" in item)

        answer = params.get("answer")
        correct = params.get("correct")
        question_id = params.get("question")
        mode = params.get("mode", "quiz")

        if None in [answer, correct, question_id]:
            raise ValueError("Missing data in postback")

        answered = get_answered_questions(user_id, mode, token)
        if question_id in answered:
            reply_message(user_id, "⛔️ คุณได้ตอบคำถามนี้ไปแล้ว", token=token)
            return

        is_correct = answer.strip() == correct.strip()
        score = update_or_add_user_score(user_id, name, is_correct)

        # 🔒 บันทึกหลังตอบ
        if mode == "math":
            record_question_history(user_id, question_id, "math")
        elif mode == "match":
            record_question_history(user_id, question_id, "match")
        elif mode == "proverb":
            record_question_history(user_id, question_id, "proverb")

        feedback = (
            f"✅ ถูกต้อง! คุณได้ 1 คะแนน (รวม {score} คะแนน)"
            if is_correct else
            f"❌ คำตอบที่ถูกคือ: {correct}\nคะแนนคุณคือ {score}"
        )
        reply_message(user_id, feedback, token=token)

        if mode == "math":
            send_question(user_id, key="math", token=token)
        elif mode == "match":
            send_question(user_id, key="match", token=token)
        elif mode == "proverb":
            send_question(user_id, key="proverb", token=token)

    except Exception as e:
        print(f"⚠️ ERROR handling postback: {e}")
    finally:
            processing_users[user_id] = False