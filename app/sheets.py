from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("google-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

def get_user_score(user_id):
    rows = sheet.get_all_records()
    for i, row in enumerate(rows):
        if row.get("userId") == user_id:
            return i + 2, row 
    return None, None

def update_or_add_user_score(user_id, name, is_correct):
    row_index, existing_row = get_user_score(user_id)
    score = 10 if is_correct else 0

    if existing_row:
        new_score = int(existing_row["score"]) + score
        sheet.update_cell(row_index, 3, new_score)
    else:
        sheet.append_row([user_id, name, score])
        
def load_quiz_questions():
    questions_sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("questions")
    rows = questions_sheet.get_all_records()

    quiz_data = []
    for row in rows:
        question = row.get("question")
        choices = [c.strip() for c in row.get("choices", "").split(",")]
        answer = row.get("answer")
        if question and choices and answer:
            quiz_data.append({
                "question": question,
                "choices": choices,
                "answer": answer
            })
    return quiz_data