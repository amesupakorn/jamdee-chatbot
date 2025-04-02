import random
import requests
import os
import json
from dotenv import load_dotenv
from app.components.finished_card import generate_finished_message
from app.components.send_game_menu import load_game_menu_from_sheet
from app.quiz_match import get_unanswered_match_question
from app.quiz_math import get_answered_math_questions, get_unanswered_math_question, load_math_questions, record_math_history
from app.quiz_proverb import get_unanswered_proverb_question
from app.scores import get_user_score, get_user_score_sum, update_or_add_user_score
from app.components.quiz_flex import generate_quiz_flex

load_dotenv()
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")


def reply_message(user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, data=json.dumps(data))
    




def get_user_profile(user_id):
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # มี displayName, userId, pictureUrl
    else:
        return {}
    
def send_game_menu(user_id):
    flex = load_game_menu_from_sheet()

    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer " + LINE_ACCESS_TOKEN
        },
        data=json.dumps({
            "to": user_id,
            "messages": [flex]
        })
    )


def send_score_card(user_id):
    profile = get_user_profile(user_id)
    display_name = profile.get("displayName", "คุณผู้ใช้")
    picture_url = profile.get("pictureUrl", "https://i.imgur.com/UePbdph.png")  # fallback
    score = get_user_score_sum(user_id)

    flex = {
    "type": "flex",
    "altText": "คะแนนของคุณ",
    "contents": {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "🏆 คะแนนสะสม 🏆",
                    "align": "center",
                    "weight": "bold",
                    "color": "#FF6A4B",  # ปรับสีตามธีม
                    "size": "xl"
                }
            ],
            "backgroundColor": "#FFECE8",  # พื้นหัวอ่อน
            "paddingAll": "md"
        },
        "hero": {
            "type": "image",
            "url": picture_url,
            "size": "full",
            "aspectRatio": "1:1",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"{display_name}",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "color": "#FF6A4B",  # ชื่อ
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{score}",
                            "weight": "bold",
                            "size": "3xl",
                            "align": "center",
                            "color": "#C62828"  # สีแดงเข้ม อ่านง่าย
                        },
                        {
                            "type": "text",
                            "text": "คะแนน",
                            "weight": "bold",
                            "size": "lg",
                            "align": "center",
                            "color": "#C62828",
                            "margin": "xs"
                        }
                    ],
                    "backgroundColor": "#FFF3F0",  # พื้นในกล่องคะแนน
                    "cornerRadius": "lg",
                    "paddingAll": "lg",
                    "margin": "lg"
                },
                {
                    "type": "text",
                    "text": "เก่งมากเลย! มาลุ้นต่อกันนะ 🎉",
                    "align": "center",
                    "size": "sm",
                    "color": "#555555",
                    "margin": "xl",
                    "weight": "bold"
                }
            ],
            "paddingAll": "xl",
            "backgroundColor": "#FFFFFF"
        }
    }


    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [flex]
    }
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps(data))
    


def send_math_question(user_id):
    profile = get_user_profile(user_id)
    display_name = profile.get("displayName", "ผู้ใช้")
    picture_url = profile.get("pictureUrl", "https://i.imgur.com/UePbdph.png")  # fallback รูปสำรอง
    question = get_unanswered_math_question(user_id)
    if not question:
        flex_message = generate_finished_message(display_name, picture_url, category="math")
        requests.post("https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
        },
        data=json.dumps({
            "to": user_id,
            "messages": [flex_message]
        }))
        return 

    question["mode"] = "math"
    flex = generate_quiz_flex(question, header_title="➕ เกมคณิตศาสตร์")

    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={ "Authorization": f"Bearer {LINE_ACCESS_TOKEN}", "Content-Type": "application/json" },
        data=json.dumps({ "to": user_id, "messages": [flex] })
    )
    

def send_match_question(user_id):
    profile = get_user_profile(user_id)
    display_name = profile.get("displayName", "ผู้ใช้")
    picture_url = profile.get("pictureUrl", "https://i.imgur.com/UePbdph.png")  # fallback รูปสำรอง
    quiz = get_unanswered_match_question(user_id)
    if not quiz:
        flex_message = generate_finished_message(display_name, picture_url, category="match")
        requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
        },
        data=json.dumps({
            "to": user_id,
            "messages": [flex_message]
        })
        )
        return 

    
    # Create styled choice buttons
    quiz["mode"] = "match"
    flex = generate_quiz_flex(quiz, header_title="🐾 เกมทายเงาสัตว์")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [flex]
    }
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps(data))
    

def send_proverb_question(user_id):
    profile = get_user_profile(user_id)
    display_name = profile.get("displayName", "ผู้ใช้")
    picture_url = profile.get("pictureUrl", "https://i.imgur.com/UePbdph.png")  # fallback รูปสำรอง
    quiz = get_unanswered_proverb_question(user_id)
    if not quiz:
        flex_message = generate_finished_message(display_name, picture_url, category="proverb")
        requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
        },
        data=json.dumps({
            "to": user_id,
            "messages": [flex_message]
        })
        )
        return 

    
    # Create styled choice buttons
    quiz["mode"] = "proverb"
    flex = generate_quiz_flex(quiz, header_title="🔍 เกมทายสุภาษิต")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [flex]
    }
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps(data))
    
