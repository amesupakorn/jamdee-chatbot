import requests
import json
from dotenv import load_dotenv
import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import os
import json


from app.components.convert_image import convert_drive_link

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
google_json_path = os.getenv("GOOGLE_JSON_PATH")
creds = ServiceAccountCredentials.from_json_keyfile_name(google_json_path, scope)
client = gspread.authorize(creds)



def load_game_menu_from_sheet():
    worksheet = client.open_by_key(GOOGLE_SHEET_ID).worksheet("games")
    rows = worksheet.get_all_records()

    bubbles = []

    for game in rows:
        bubble = {
            "type": "bubble",
            "size": "kilo",
            "hero": {
                "type": "image",
                "url": convert_drive_link(game["image_url"]),
                "size": "full",
                "aspectRatio": "1:1",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": game["name"],
                        "wrap": True,
                        "weight": "bold",
                        "size": "sm"
                    },
                    {
                        "type": "text",
                        "text": f"ระดับ: {game['level']}",
                        "size": "xs",
                        "color": "#999999"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": "#FF6A4B",
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": game["button_label"],
                            "text": game["button_text"]
                        }
                    }
                ]
            }
        }

        bubbles.append(bubble)

    flex_message = {
        "type": "flex",
        "altText": "เลือกเกมที่อยากเล่น",
        "contents": {
            "type": "carousel",
            "contents": bubbles
        }
    }

    return flex_message



