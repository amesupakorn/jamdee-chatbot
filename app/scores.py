from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json


load_dotenv()
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_json = os.getenv("GOOGLE_SERVICE_JSON")
creds_dict = json.loads(google_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("scores")

def get_user_score(user_id):
    rows = sheet.get_all_records()
    for i, row in enumerate(rows):
        if row.get("userId") == user_id:
            return i + 2, row 
    return None, None

def get_user_score_sum(user_id):
    rows = sheet.get_all_records()
    for row in rows:
        if row.get("userId") == user_id:
            return int(row.get("score", 0))
    return 0  # ถ้าไม่เจอ

def update_or_add_user_score(user_id, name, is_correct):
    row_index, existing_row = get_user_score(user_id)
    score = 1 if is_correct else 0

    if existing_row:
        new_score = int(existing_row["score"]) + score
        sheet.update_cell(row_index, 3, new_score)
        return new_score
    else:
        sheet.append_row([user_id, name, score])
        return score
    
def reset_user_score(user_id):
    sheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("scores")
    rows = sheet.get_all_records()
    for i, row in enumerate(rows):
        if row.get("userId") == user_id:
            sheet.update_cell(i + 2, 3, 0) 
            break

