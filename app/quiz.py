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
questions_sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("match_questions")

def load_questions(topic):
    try:
        sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(f"{topic}_questions")
        rows = sheet.get_all_records(expected_headers=[
            "question", "image_url", "choice1", "choice2", "choice3", "answer"
        ])    
    except gspread.exceptions.GSpreadException as e:
        print(f"❌ Error loading {topic}_questions: {e}")
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

        if len(choices) < 2:
            continue

        try:
            answer_index = int(str(row.get("answer", "1")).strip()) - 1
        except ValueError:
            continue

        if 0 <= answer_index < len(choices):
            questions.append({
                "id": question_id,
                "question": question_text,
                "image_url": image_url,
                "choices": choices,
                "answer": choices[answer_index],
                "mode": topic
            })

    return questions

def get_answered_questions(user_id, topic):
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(f"{topic}_history")
    rows = sheet.get_all_records()
    return [row["questionId"] for row in rows if row["userId"] == user_id]

def record_question_history(user_id, question_id, topic):
    print(f"📥 record to history: user={user_id}, qid={question_id}")
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet(f"{topic}_history")
    sheet.append_row([user_id, question_id])

def get_unanswered_question(user_id, topic):
    all_questions = load_questions(topic)
    answered_ids = get_answered_questions(user_id, topic)

    available = [q for q in all_questions if q["id"] not in answered_ids]

    if not available:
        return None

    return random.choice(available)