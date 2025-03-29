from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import random

load_dotenv()
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)
questions_sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("questions")

def load_quiz_questions():
    rows = questions_sheet.get_all_records()
    quiz_data = []

    for row in rows:
        question = str(row.get("question", "")).strip()
        answer = str(row.get("answer", "")).strip()

        # ✅ สร้าง choices จากคอลัมน์ที่ขึ้นต้นด้วย "choice"
        choices = [
            str(row[key]).strip()
            for key in row
            if key.lower().startswith("choice") and row[key]
        ]

        # ✅ Validation
        if not question or not answer or len(choices) < 2:
            continue

        quiz_data.append({
            "question": question,
            "choices": choices,
            "answer": answer
        })

    return quiz_data

def get_random_question():
    all_questions = load_quiz_questions()
    return random.choice(all_questions) if all_questions else None

def get_unanswered_question(user_id):
    questions_sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("questions")
    history_sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("history")

    all_questions = load_quiz_questions()
    print("== loaded questions ==")
    for q in all_questions:
        print(q)  # 👈 ดูว่าแต่ละ dict มี key อะไรบ้าง

    history_rows = history_sheet.get_all_records()
    seen = [row["question"] for row in history_rows if row["userId"] == user_id]
    available = [q for q in all_questions if q["question"] not in seen]

    if not available:
        return None

    selected = random.choice(available)
    return selected
def record_question_history(user_id, question):
    history_sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("history")
    history_sheet.append_row([user_id, question])