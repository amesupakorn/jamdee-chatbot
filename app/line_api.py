import requests
import os
import json
from dotenv import load_dotenv
from app.quiz import get_unanswered_question, record_question_history

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
    
def send_quiz(user_id):
    profile = get_user_profile(user_id)
    display_name = profile.get("displayName", "ผู้ใช้")
    picture_url = profile.get("pictureUrl", "https://i.imgur.com/UePbdph.png")  # fallback รูปสำรอง
    quiz = get_unanswered_question(user_id)
    if not quiz:
        # Send a celebratory message with confetti emoji and styling
        celebration_message = {
            "type": "flex",
            "altText": "คุณตอบครบทุกคำถามแล้ว!",
            "contents": {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "🎊 ยินดีด้วย! 🎊",
                            "weight": "bold",
                            "size": "xl",
                            "align": "center",
                            "color": "#1DB446"
                        },
                        {
                            "type": "text",
                            "text": "คุณตอบครบทุกคำถามแล้ว!",
                            "weight": "bold",
                            "size": "lg",
                            "align": "center",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "ขอบคุณที่ร่วมสนุกกับเรา",
                            "size": "md",
                            "align": "center",
                            "margin": "md",
                            "color": "#555555"
                        }
                    ],
                    "backgroundColor": "#FFFDE7",
                    "paddingAll": "xl"
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "action": {
                                "type": "message",
                                "label": "เริ่มเล่นใหม่",
                                "text": "เริ่มใหม่"
                            },
                            "style": "primary",
                            "color": "#1DB446"
                        }
                    ]
                }
            }
        }
        
        finished_message = {
            "type": "flex",
            "altText": "คุณตอบครบแล้ว!",
            "contents": {
                "type": "bubble",
                "header": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "นั่งไว้",
                            "align": "center",
                            "weight": "bold",
                            "color": "#FFFFFF",
                            "size": "lg"
                        }
                    ],
                    "backgroundColor": "#FF69B4",
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
                            "text": display_name,
                            "align": "center",
                            "weight": "bold",
                            "size": "md",
                            "margin": "md"
                        },
                        {
                            "type": "text",
                            "text": "คำถามหมดแล้วสำหรับวันนี้ กรุณากลับมาใหม่ในวันพรุ่งนี้นะค้าบ😊",
                            "wrap": True,
                            "align": "center",
                            "margin": "md",
                            "size": "sm",
                            "color": "#444444"
                        }
                    ],
                    "paddingAll": "md"
                }
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
        }
        data = {
            "to": user_id,
            "messages": [finished_message]
        }
        requests.post("https://api.line.me/v2/bot/message/push", headers=headers, data=json.dumps(data))
        return

    
    # Create styled choice buttons
    choice_buttons = []
    for i, c in enumerate(quiz["choices"]):
        choice_buttons.append(
           {
                "type": "button",
                "action": {
                    "type": "postback", 
                    "label": c, 
                    "data": f"answer={c}|correct={quiz['answer']}|question={quiz['question']}"
                },
                "style": "primary",
                "color": "#FFB6C1",
                "height": "sm",
                "margin": "md"
            }
        )
        # Add separator after each button except the last one
        if i < len(quiz["choices"]) - 1:
            choice_buttons.append(
                {
                    "type": "separator",
                    "margin": "sm"
                }
            )
    
    # Create a nice looking quiz flex message with better styling
    flex = {
        "type": "flex",
        "altText": "คำถามมาแล้ว!",
        "contents": {
            "type": "bubble",
           "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                    "type": "text",
                    "text": "🧠 คำถามแสนสนุก",
                    "weight": "bold",
                    "size": "xl",
                    "align": "center",
                    "color": "#FF69B4"
                    }
                ],
                "backgroundColor": "#DDF4FF",
                "paddingAll": "lg"
                },
            "hero": {
                "type": "image",
                "url": "https://scdn.line-apps.com/n/channel_devcenter/img/fx/01_2_restaurant.png", # Replace with your quiz image
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": quiz["question"],
                        "weight": "bold",
                        "size": "lg",
                        "wrap": True,
                        "margin": "md"
                    },
                    {
                        "type": "text",
                        "text": "เลือกคำตอบที่ถูกต้อง",
                        "size": "sm",
                        "color": "#555555",
                        "margin": "md"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": choice_buttons,
                        "margin": "xl"
                    }
                ],
                "paddingAll": "xl"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "ตอบคำถามเพื่อสะสมคะแนน",
                        "size": "xs",
                        "color": "#AAAAAA",
                        "align": "center"
                    }
                ],
                "paddingAll": "lg"
            },
            "styles": {
                "body": {
                    "backgroundColor": "#F5F5F7"
                }
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
    
