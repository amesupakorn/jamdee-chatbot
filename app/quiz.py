import os
import json
import time
import gspread
import random
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from app.components.convert_image import convert_drive_link

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
CACHE_FOLDER = "cache"
os.makedirs(CACHE_FOLDER, exist_ok=True)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)

# === 🔁 Cache utility ===
def is_cache_expired(filepath, ttl_seconds=300):
    return not os.path.exists(filepath) or (time.time() - os.path.getmtime(filepath)) > ttl_seconds

# === 📥 โหลดคำถามจาก cache (หรือ Google Sheet ถ้าไม่มี) ===
def load_questions(topic, use_cache=True):
    cache_path = os.path.join(CACHE_FOLDER, f"{topic}_questions.json")

    if use_cache and not is_cache_expired(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(f"{topic}_questions")
        rows = sheet.get_all_records(expected_headers=[
            "question", "image_url", "choice1", "choice2", "choice3", "answer"
        ])
    except Exception as e:
        print(f"❌ Error loading {topic}_questions from sheet: {e}")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                print("🔁 Using stale cache as fallback")
                return json.load(f)
        return []

    questions = []
    for idx, row in enumerate(rows):
        question_id = f"{topic}_{idx+1}"
        question_text = str(row.get("question", "")).strip()
        image_url = convert_drive_link(row.get("image_url", ""))

        choices = [
            str(value).strip()
            for key, value in row.items()
            if key.lower().startswith("choice") and str(value).strip()
        ]

        try:
            answer_index = int(str(row.get("answer", "1")).strip()) - 1
        except ValueError:
            continue

        if len(choices) >= 2 and 0 <= answer_index < len(choices):
            questions.append({
                "id": question_id,
                "question": question_text,
                "image_url": image_url,
                "choices": choices,
                "answer": choices[answer_index],
                "mode": topic
            })

    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)

    return questions

def get_answered_questions(user_id, topic):
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(f"{topic}_history")
    rows = sheet.get_all_records()
    return [row["questionId"] for row in rows if row["userId"] == user_id]

def record_question_history(user_id, question_id, topic):
    print(f"📥 record to history: user={user_id}, qid={question_id}")
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(f"{topic}_history")
    sheet.append_row([str(user_id), str(question_id)])

def get_unanswered_question(user_id, topic):
    all_questions = load_questions(topic)
    answered_ids = get_answered_questions(user_id, topic)
    available = [q for q in all_questions if q["id"] not in answered_ids]
    return random.choice(available) if available else None