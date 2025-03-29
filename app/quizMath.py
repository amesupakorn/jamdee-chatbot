
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import random

from app.components.convert_image import convert_drive_link

load_dotenv()
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)

def load_math_questions():
    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("math_questions")
        rows = sheet.get_all_records(expected_headers=[
            "question", "image_url", "choice1", "choice2", "choice3", "answer"
        ])    
    except gspread.exceptions.GSpreadException as e:
        print(f"❌ Error loading math_questions: {e}")
        return []

    questions = []
    for row in rows:
        question_text = str(row.get("question", "")).strip()
        image_url = convert_drive_link(row.get("image_url", ""))

        # ดึงตัวเลือกทั้งหมดที่ขึ้นต้นด้วย 'choice'
        choices = [
            str(value).strip()
            for key, value in row.items()
            if key.lower().startswith("choice") and str(value).strip()
        ]

        try:
            answer_index = int(str(row.get("answer", "1")).strip()) - 1
        except ValueError:
            continue  

        if question_text and all(choices) and 0 <= answer_index < len(choices):
            questions.append({
                "question": question_text,
                "image_url": image_url,
                "choices": choices,
                "answer": choices[answer_index],
                "mode": "math"
            })

    return questions

def get_answered_math_questions(user_id):
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("math_history")
    rows = sheet.get_all_records()
    return [row["question"] for row in rows if row["userId"] == user_id]

def record_math_history(user_id, question_text):
    print(f"📥 record to history: user={user_id}, q={question_text}")
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("math_history")
    sheet.append_row([user_id, question_text])
    
def get_unanswered_math_question(user_id):
    all_questions = load_math_questions()
    answered = get_answered_math_questions(user_id)

    available = [q for q in all_questions if q["question"] not in answered]

    if not available:
        return None 

    return random.choice(available)