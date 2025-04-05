import random
import requests
import os
import json
from dotenv import load_dotenv
from app.components.finished_card import generate_finished_message
from app.components.send_game_menu import load_game_menu_from_sheet
from app.quiz import get_unanswered_question
from app.scores import get_user_score, get_user_score_sum, update_or_add_user_score
from app.components.quiz_flex import generate_quiz_flex


import requests

def start_loading_animation(user_id, token):
    url = "https://api.line.me/v2/bot/chat/loading/start"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "chatId": user_id,
        "loadingSeconds": min(5, 10) 
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error starting loading animation: {e}")
        return {"error": str(e)}

def reply_message(user_id, message, token):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    requests.post(url, headers=headers, data=json.dumps(data))
    




def get_user_profile(user_id, token):
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # มี displayName, userId, pictureUrl
    else:
        return {}
    
def send_game_menu(user_id, token):
    flex = load_game_menu_from_sheet()

    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer " + token
        },
        data=json.dumps({
            "to": user_id,
            "messages": [flex]
        })
    )


def send_score_card(user_id, token):
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
        "Authorization": f"Bearer {token}"
    }
    data = {
        "to": user_id,
        "messages": [flex]
    }
    requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps(data))

topic_title_map = {
    "math": "➕ เกมคณิตศาสตร์",
    "match": "🐾 เกมทายเงาสัตว์",
    "proverb": "🔍 เกมทายสุภาษิต",
}

def send_question(user_id, key, token):
    profile = get_user_profile(user_id)
    display_name = profile.get("displayName", "ผู้ใช้")
    picture_url = profile.get("pictureUrl", "https://i.imgur.com/UePbdph.png")  # fallback รูปสำรอง
    question = get_unanswered_question(user_id, topic=key)
    if not question:
        flex_message = generate_finished_message(display_name, picture_url, category=key)
        requests.post("https://api.line.me/v2/bot/message/push",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        data=json.dumps({
            "to": user_id,
            "messages": [flex_message]
        }))
        return 

    header_title = topic_title_map.get(key, "❓ เกมคำถาม") 
    question["mode"] = key
    flex = generate_quiz_flex(question, header_title=header_title)

    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={ "Authorization": f"Bearer {token}", "Content-Type": "application/json" },
        data=json.dumps({ "to": user_id, "messages": [flex] })
    )